from pathlib import Path


def main():
    root = Path("datasets")
    missing = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        name = folder.name
        expected = [
            folder / f"{name}.csv",
            folder / f"{name}_train.csv",
            folder / f"{name}_test.csv",
            folder / f"{name}_rf.pkl",
        ]
        for path in expected:
            if not path.exists():
                missing.append(str(path))
    if missing:
        print("Missing files:")
        for item in missing:
            print(" -", item)
    else:
        print("Dataset layout looks complete.")


if __name__ == "__main__":
    main()

