from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


SELECTORS = ["info_gain", "shapley", "p_value", "random_node", "modal"]
TREE_COUNTS = [5, 10]


def dataset_names(datasets_dir: Path) -> list[str]:
    names = []
    for folder in sorted(p for p in datasets_dir.iterdir() if p.is_dir()):
        name = folder.name
        if (folder / f"{name}_rf.pkl").exists():
            names.append(name)
    return names


def parse_csv(text: str, cast=str) -> list:
    return [cast(part.strip()) for part in text.split(",") if part.strip()]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    fieldnames = list(row.keys())
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def read_if_exists(path: Path) -> pd.DataFrame | None:
    if path.exists() and path.stat().st_size > 0:
        try:
            return pd.read_csv(path)
        except EmptyDataError:
            return None
    return None


def status_path(run_dir: Path) -> Path:
    return run_dir / "status.csv"


def read_status(run_dir: Path) -> dict | None:
    frame = read_if_exists(status_path(run_dir))
    if frame is None or frame.empty:
        return None
    return frame.iloc[-1].to_dict()


def write_status(run_dir: Path, row: dict) -> None:
    write_csv(status_path(run_dir), [row])


def collect_outputs(out_dir: Path) -> None:
    summary_frames = []
    ranking_frames = []
    robustness_frames = []
    failure_rows = []
    status_rows = []

    for summary_path in out_dir.glob("*/trees_*/B_*/selector_*/summary.csv"):
        frame = read_if_exists(summary_path)
        if frame is None:
            continue
        frame["run_dir"] = str(summary_path.parent)
        summary_frames.append(frame)

    for ranking_path in out_dir.glob("*/trees_*/B_*/selector_*/rankings.csv"):
        run_dir = ranking_path.parent
        frame = read_if_exists(ranking_path)
        if frame is None:
            continue
        frame["dataset"] = run_dir.parents[2].name
        frame["trees"] = run_dir.parents[1].name.replace("trees_", "")
        frame["budget"] = run_dir.parents[0].name.replace("B_", "")
        frame["selector"] = run_dir.name.replace("selector_", "")
        ranking_frames.append(frame)

    for robustness_path in out_dir.glob("*/trees_*/B_*/selector_*/robustness.csv"):
        run_dir = robustness_path.parent
        frame = read_if_exists(robustness_path)
        if frame is None:
            continue
        frame["dataset"] = run_dir.parents[2].name
        frame["trees"] = run_dir.parents[1].name.replace("trees_", "")
        frame["budget"] = run_dir.parents[0].name.replace("B_", "")
        frame["selector"] = run_dir.name.replace("selector_", "")
        robustness_frames.append(frame)

    for error_path in out_dir.glob("*/trees_*/B_*/selector_*/error.txt"):
        run_dir = error_path.parent
        status = read_status(run_dir) or {}
        failure_rows.append(
            {
                "dataset": run_dir.parents[2].name,
                "trees": run_dir.parents[1].name.replace("trees_", ""),
                "budget": run_dir.parents[0].name.replace("B_", ""),
                "selector": run_dir.name.replace("selector_", ""),
                "status": status.get("status", "failed"),
                "elapsed_seconds": status.get("elapsed_seconds", ""),
                "timeout_seconds": status.get("timeout_seconds", ""),
                "run_dir": str(run_dir),
                "error": error_path.read_text(encoding="utf-8", errors="replace"),
            }
        )

    for status_file in out_dir.glob("*/trees_*/B_*/selector_*/status.csv"):
        frame = read_if_exists(status_file)
        if frame is None or frame.empty:
            continue
        row = frame.iloc[-1].to_dict()
        row["run_dir"] = str(status_file.parent)
        status_rows.append(row)

    if summary_frames:
        pd.concat(summary_frames, ignore_index=True).to_csv(out_dir / "ALL_SUMMARIES.csv", index=False)
    if ranking_frames:
        pd.concat(ranking_frames, ignore_index=True).to_csv(out_dir / "ALL_RANKINGS.csv", index=False)
    if robustness_frames:
        pd.concat(robustness_frames, ignore_index=True).to_csv(out_dir / "ALL_ROBUSTNESS.csv", index=False)
    write_csv(out_dir / "FAILURES.csv", failure_rows)
    write_csv(out_dir / "RUN_STATUS_ALL.csv", status_rows)
    write_experiment_report(out_dir, status_rows, failure_rows)


def write_experiment_report(out_dir: Path, status_rows: list[dict], failure_rows: list[dict]) -> None:
    completed = [r for r in status_rows if r.get("status") in {"completed", "skipped_existing"}]
    timed_out = [r for r in status_rows if r.get("status") == "timeout"]
    failed = [r for r in status_rows if r.get("status") == "failed"]
    skipped = [r for r in status_rows if str(r.get("status", "")).startswith("skipped")]

    lines = [
        "# BDSS Experiment Report",
        "",
        "This report is generated automatically by `scripts/run_all_54_experiments.py`.",
        "",
        "## Summary",
        "",
        f"- Total recorded runs: {len(status_rows)}",
        f"- Completed or already completed: {len(completed)}",
        f"- Timed out: {len(timed_out)}",
        f"- Failed: {len(failed)}",
        f"- Skipped on resume: {len(skipped)}",
        "",
        "A timeout means the run exceeded the configured threshold, was stopped, recorded, and the script continued to the next dataset/tree/selector combination.",
        "",
    ]

    if timed_out:
        lines.extend(["## Timed Out Runs", ""])
        for row in timed_out:
            lines.append(
                f"- {row.get('dataset')} | trees={row.get('trees')} | selector={row.get('selector')} | "
                f"budget={row.get('budget')} | stopped after {row.get('timeout_seconds')} seconds"
            )
        lines.append("")

    if failed:
        lines.extend(["## Failed Runs", ""])
        for row in failed:
            lines.append(
                f"- {row.get('dataset')} | trees={row.get('trees')} | selector={row.get('selector')} | "
                f"budget={row.get('budget')} | see error.txt in {row.get('run_dir', '')}"
            )
        lines.append("")

    lines.extend(
        [
            "## Output Files",
            "",
            "- `ALL_SUMMARIES.csv`: successful construction summaries",
            "- `ALL_RANKINGS.csv`: variable rankings for successful runs",
            "- `ALL_ROBUSTNESS.csv`: robustness rows if robustness samples were enabled",
            "- `RUN_STATUS_ALL.csv`: one status row per attempted run",
            "- `FAILURES.csv`: timeout/failure details",
            "- each run folder contains `run.log`, and failed/timeout runs contain `error.txt`",
            "",
        ]
    )
    (out_dir / "EXPERIMENT_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def final_status_row(
    name: str,
    trees: int,
    budget: int,
    selector: str,
    status: str,
    run_dir: Path,
    elapsed_seconds: float | str = "",
    timeout_seconds: int | None = None,
    message: str = "",
) -> dict:
    return {
        "dataset": name,
        "trees": trees,
        "budget": budget,
        "selector": selector,
        "status": status,
        "elapsed_seconds": elapsed_seconds,
        "timeout_seconds": timeout_seconds or "",
        "run_dir": str(run_dir),
        "message": message,
    }


def run_one(
    project_dir: Path,
    datasets_dir: Path,
    out_dir: Path,
    name: str,
    trees: int,
    budget: int,
    selector: str,
    max_test_samples: int,
    seed: int,
    timeout_seconds: int | None,
    retry_failures: bool,
) -> dict:
    run_dir = out_dir / name / f"trees_{trees}" / f"B_{budget}" / f"selector_{selector}"
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.csv"
    log_path = run_dir / "run.log"
    error_path = run_dir / "error.txt"

    if summary_path.exists() and summary_path.stat().st_size > 0:
        row = final_status_row(name, trees, budget, selector, "skipped_existing", run_dir)
        write_status(run_dir, row)
        return row

    previous_status = read_status(run_dir)
    if previous_status and previous_status.get("status") in {"timeout", "failed"} and not retry_failures:
        previous_status["status"] = f"skipped_previous_{previous_status.get('status')}"
        write_status(run_dir, previous_status)
        return previous_status

    if error_path.exists():
        error_path.unlink()

    cmd = [
        sys.executable,
        "-m",
        "bdss_rf_robustness.cli",
        "run-one",
        "--datasets",
        str(datasets_dir),
        "--name",
        name,
        "--trees",
        str(trees),
        "--budget",
        str(budget),
        "--selector",
        selector,
        "--max-test-samples",
        str(max_test_samples),
        "--seed",
        str(seed),
        "--out",
        str(run_dir),
    ]

    started = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=project_dir,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        elapsed = time.perf_counter() - started
        log_path.write_text(
            "COMMAND:\n"
            + " ".join(cmd)
            + "\n\nSTDOUT:\n"
            + proc.stdout
            + "\n\nSTDERR:\n"
            + proc.stderr,
            encoding="utf-8",
        )
        if proc.returncode != 0:
            error_path.write_text(proc.stderr or proc.stdout or "Unknown error", encoding="utf-8")
            row = final_status_row(
                name, trees, budget, selector, "failed", run_dir, elapsed, timeout_seconds, "process returned non-zero"
            )
            write_status(run_dir, row)
            return row
        row = final_status_row(name, trees, budget, selector, "completed", run_dir, elapsed, timeout_seconds)
        write_status(run_dir, row)
        return row
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        message = f"Timeout after {timeout_seconds} seconds\n\nSTDOUT:\n{exc.stdout}\n\nSTDERR:\n{exc.stderr}"
        log_path.write_text(message, encoding="utf-8")
        error_path.write_text(message, encoding="utf-8")
        row = final_status_row(
            name,
            trees,
            budget,
            selector,
            "timeout",
            run_dir,
            elapsed,
            timeout_seconds,
            f"stopped after threshold of {timeout_seconds} seconds",
        )
        write_status(run_dir, row)
        return row


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all 54 datasets with 5 and 10 trees and all five selectors."
    )
    parser.add_argument("--datasets", default="datasets", help="Path to the datasets folder.")
    parser.add_argument("--out", default="results/full_54_grid", help="Output folder for all records.")
    parser.add_argument("--budget", type=int, default=20000, help="BDD node budget for every run.")
    parser.add_argument(
        "--max-test-samples",
        type=int,
        default=10,
        help="How many test samples to use for robustness per dataset. Use 0 to skip robustness.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Per-run time limit in seconds. 0 means no timeout. Default: 600.",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--retry-failures", action="store_true", help="Retry runs that already failed or timed out.")
    parser.add_argument(
        "--limit-datasets",
        type=int,
        default=0,
        help="Use only the first N datasets. 0 means all datasets.",
    )
    parser.add_argument(
        "--tree-counts",
        default="5,10",
        help="Comma-separated tree counts. Default: 5,10.",
    )
    parser.add_argument(
        "--selectors",
        default="info_gain,shapley,p_value,random_node,modal",
        help="Comma-separated selectors.",
    )
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parents[1]
    datasets_dir = (project_dir / args.datasets).resolve()
    out_dir = (project_dir / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    timeout_seconds = args.timeout_seconds if args.timeout_seconds > 0 else None
    
    names = dataset_names(datasets_dir)

    # Skip datasets that previously timed out or failed
    SKIP_DATASETS = {
        "ann-thyroid",
        "biodegradation",
        "breast-cancer-wisconsin",
        "cloud",
        "diabetes",
        "factors",
        "fourier",
        "glass",
        "ionosphere",
        "karhunen",
        "letter",
        "magic",
        "messidor",
        "pendigits",
        "phoneme",
        "pima",
        "ring",
        "segmentation",
        "shuttle",
        "sonar",
        "spambase",
        "spectf",
        "texture",
        "twonorm",
        "vehicle",
        "vowel",
        "waveform-21",
        "waveform-40",
        "wdbc",
        "wine-quality-red",
        "wine-quality-white",
        "wine-recog",
        "wine-recognition",
        "wpbc",
        "zernike",
    }

    names = [name for name in names if name not in SKIP_DATASETS]

    print(f"Skipping {len(SKIP_DATASETS)} datasets.")
    print(f"Running {len(names)} datasets.")
    
    
    
    if args.limit_datasets > 0:
        names = names[: args.limit_datasets]
    tree_counts = parse_csv(args.tree_counts, int)
    selectors = parse_csv(args.selectors, str)
    total = len(names) * len(tree_counts) * len(selectors)
    done = 0
    print(f"Found {len(names)} datasets.")
    print(f"Tree counts: {tree_counts}")
    print(f"Selectors: {selectors}")
    print(f"Total runs: {total} = datasets x tree counts x selectors")
    print(f"Results folder: {out_dir}")

    for name in names:
        for trees in tree_counts:
            for selector in selectors:
                done += 1
                print(f"[{done}/{total}] {name} | trees={trees} | selector={selector}")
                row = run_one(
                    project_dir=project_dir,
                    datasets_dir=datasets_dir,
                    out_dir=out_dir,
                    name=name,
                    trees=trees,
                    budget=args.budget,
                    selector=selector,
                    max_test_samples=args.max_test_samples,
                    seed=args.seed,
                    timeout_seconds=timeout_seconds,
                    retry_failures=args.retry_failures,
                )
                append_csv(out_dir / "RUN_MANIFEST.csv", row)
                collect_outputs(out_dir)

    collect_outputs(out_dir)
    print("Finished.")
    print(f"Combined summary: {out_dir / 'ALL_SUMMARIES.csv'}")
    print(f"Combined rankings: {out_dir / 'ALL_RANKINGS.csv'}")
    print(f"Combined robustness: {out_dir / 'ALL_ROBUSTNESS.csv'}")
    print(f"Run manifest: {out_dir / 'RUN_MANIFEST.csv'}")
    print(f"Failures, if any: {out_dir / 'FAILURES.csv'}")


if __name__ == "__main__":
    main()
