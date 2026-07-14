# BDSS Random-Forest Robustness Project

This project implements the pipeline requested in the BDSS assignment:

- load a trained random forest from `datasets/<name>/<name>_rf.pkl`
- extract the forest-induced discretization
- encode feature cells as binary bits
- build exact OBDDs for tree path formulas
- compose trees progressively
- split the accumulator with a configurable budget
- compare five split selectors
- compute model counts, variable rankings, and test-set robustness radii

The code is designed for the provided `datasets.zip` layout.

## 1. Install

Create a Python environment and install:

```bash
pip install -r requirements.txt
```

The local Codex environment used to create this package did not include
`scikit-learn` or `joblib`, so the project code was written but the `.pkl`
models could not be executed here. On your machine, install the requirements
above before running the experiments.

## 2. Dataset Layout

Expected structure:

```text
datasets/
  iris/
    iris.csv
    iris_train.csv
    iris_test.csv
    iris_rf.pkl
```

## 3. Quick Smoke Test

Start with a tiny prefix, as the assignment suggests:

```bash
python -m bdss_rf_robustness.cli run-one ^
  --datasets datasets ^
  --name iris ^
  --trees 3 ^
  --budget 20000 ^
  --selector modal ^
  --max-test-samples 5 ^
  --out results/iris_smoke
```

On macOS/Linux, replace `^` line continuations with `\`.

## 4. Run a Grid

```bash
python -m bdss_rf_robustness.cli run-grid ^
  --datasets datasets ^
  --budgets 10000,50000 ^
  --selectors info_gain,shapley,p_value,random_node,modal ^
  --tree-counts 5,10 ^
  --out results/grid
```

## 4b. Run the Full 54-Dataset Experiment

On Windows PowerShell, from the project folder:

```powershell
.\run_all_54_experiments.ps1
```

This runs:

```text
54 datasets x 2 tree counts (5, 10) x 5 selectors = 540 runs
```

The combined records are written to:

```text
results/full_54_grid/ALL_SUMMARIES.csv
results/full_54_grid/ALL_RANKINGS.csv
results/full_54_grid/ALL_ROBUSTNESS.csv
results/full_54_grid/RUN_MANIFEST.csv
results/full_54_grid/FAILURES.csv
```

The script is resumable. If you stop it and run it again, it skips runs that
already have a `summary.csv`.

## 5. Outputs

For each run, the code writes:

- `summary.csv`: completion, runtime, BDD size, frontier leaves
- `robustness.csv`: targeted and untargeted robustness for test samples
- `rankings.csv`: variable rankings from information gain, Shapley, and p-value

## 6. Important Notes

This is an exact OBDD implementation for the prefix that is successfully
composed. It intentionally starts small and grows, because the assignment itself
warns that full forests may be intractable.

The implementation uses a pure-Python ROBDD backend so the project is easy to
read and submit. For larger experiments, replace `bdd.py` with a CUDD-backed
library and keep the same public methods.
