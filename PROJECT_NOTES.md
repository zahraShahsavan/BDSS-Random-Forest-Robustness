# Project Notes

## What is implemented

The project contains a readable, pure-Python implementation of the main
assignment pipeline:

1. load the provided trained random forests
2. extract threshold cells
3. encode cell indices with binary bits
4. encode decision paths as ROBDD formulas
5. compose tree votes progressively
6. split large states with a budgeted frontier
7. provide five selector strategies
8. compute rankings and robustness distances

## Practical limitation

The assignment is computationally heavy. This implementation is deliberately
suited for correctness, clarity, and small-to-medium prefixes. For the full
54-model empirical study, use it to validate the pipeline, then consider moving
the BDD backend to CUDD for speed.

## First run

After installing requirements and placing the dataset folder next to this file:

```bash
python -m bdss_rf_robustness.cli run-one --datasets datasets --name iris --trees 3 --budget 20000 --selector modal --max-test-samples 5 --out results/iris_smoke
```

