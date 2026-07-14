from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from .bdd import BDDManager
from .composition import budgeted_compose, state_size
from .discretization import all_input_bits, build_feature_encodings
from .forest import load_dataset_frame, load_sklearn_forest
from .readouts import robustness_for_sample, variable_rankings


def parse_csv_list(text, cast=str):
    return [cast(x.strip()) for x in text.split(",") if x.strip()]


def run_one(args):
    datasets = Path(args.datasets)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    forest = load_sklearn_forest(datasets, args.name)
    if args.trees:
        tree_count = min(args.trees, len(forest.trees))
    else:
        tree_count = len(forest.trees)
    encodings = build_feature_encodings(forest)
    input_bits = all_input_bits(encodings)
    manager = BDDManager(input_bits)

    leaves, stats = budgeted_compose(
        manager=manager,
        forest=forest,
        encodings=encodings,
        tree_count=tree_count,
        budget=args.budget,
        selector=args.selector,
        input_bits=input_bits,
        seed=args.seed,
    )
    runtime = time.perf_counter() - started

    summary = pd.DataFrame(
        [
            {
                "dataset": args.name,
                "trees_requested": args.trees or len(forest.trees),
                "trees_composed": stats.trees_composed,
                "budget": args.budget,
                "selector": args.selector,
                "frontier_leaves": len(leaves),
                "peak_nodes": stats.peak_nodes,
                "splits": stats.splits,
                "runtime_seconds": runtime,
                "input_bits": len(input_bits),
                "labels": "|".join(map(str, forest.labels)),
            }
        ]
    )
    summary.to_csv(out / "summary.csv", index=False)

    variable_rankings(manager, leaves, input_bits).to_csv(out / "rankings.csv", index=False)

    test = load_dataset_frame(datasets, args.name, "test")
    rows = []
    for sample_id, (_, row) in enumerate(test.head(args.max_test_samples).iterrows()):
        for result in robustness_for_sample(manager, forest, leaves, encodings, row, input_bits):
            rows.append({"sample_id": sample_id, **result})
    pd.DataFrame(rows).to_csv(out / "robustness.csv", index=False)
    print(summary.to_string(index=False))


def run_grid(args):
    datasets = Path(args.datasets)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    budgets = parse_csv_list(args.budgets, int)
    selectors = parse_csv_list(args.selectors, str)
    tree_counts = parse_csv_list(args.tree_counts, int)
    dataset_names = [p.name for p in datasets.iterdir() if p.is_dir() and (p / f"{p.name}_rf.pkl").exists()]

    summaries = []
    for name in dataset_names:
        for trees in tree_counts:
            for budget in budgets:
                for selector in selectors:
                    run_dir = out / name / f"trees_{trees}" / f"B_{budget}" / selector
                    ns = argparse.Namespace(**vars(args))
                    ns.name = name
                    ns.trees = trees
                    ns.budget = budget
                    ns.selector = selector
                    ns.out = str(run_dir)
                    try:
                        run_one(ns)
                        summaries.append(pd.read_csv(run_dir / "summary.csv"))
                    except Exception as exc:
                        summaries.append(
                            pd.DataFrame(
                                [
                                    {
                                        "dataset": name,
                                        "trees_requested": trees,
                                        "budget": budget,
                                        "selector": selector,
                                        "error": repr(exc),
                                    }
                                ]
                            )
                        )
    pd.concat(summaries, ignore_index=True).to_csv(out / "all_summaries.csv", index=False)


def main():
    parser = argparse.ArgumentParser(description="BDSS random-forest robustness pipeline")
    sub = parser.add_subparsers(required=True)

    one = sub.add_parser("run-one")
    one.add_argument("--datasets", required=True)
    one.add_argument("--name", required=True)
    one.add_argument("--trees", type=int, default=5)
    one.add_argument("--budget", type=int, default=20000)
    one.add_argument("--selector", default="modal", choices=["info_gain", "shapley", "p_value", "random_node", "modal"])
    one.add_argument("--max-test-samples", type=int, default=10)
    one.add_argument("--seed", type=int, default=0)
    one.add_argument("--out", required=True)
    one.set_defaults(func=run_one)

    grid = sub.add_parser("run-grid")
    grid.add_argument("--datasets", required=True)
    grid.add_argument("--budgets", default="10000,50000")
    grid.add_argument("--selectors", default="info_gain,shapley,p_value,random_node,modal")
    grid.add_argument("--tree-counts", default="5,10")
    grid.add_argument("--max-test-samples", type=int, default=10)
    grid.add_argument("--seed", type=int, default=0)
    grid.add_argument("--out", required=True)
    grid.set_defaults(func=run_grid)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

