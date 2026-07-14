# BDSS Experiment Report

This report is generated automatically by `scripts/run_all_54_experiments.py`.

## Summary

- Total recorded runs: 190
- Completed or already completed: 167
- Timed out: 23
- Failed: 0
- Skipped on resume: 0

A timeout means the run exceeded the configured threshold, was stopped, recorded, and the script continued to the next dataset/tree/selector combination.

## Timed Out Runs

- bupa | trees=10 | selector=info_gain | budget=20000 | stopped after 300 seconds
- bupa | trees=10 | selector=modal | budget=20000 | stopped after 300 seconds
- bupa | trees=10 | selector=p_value | budget=20000 | stopped after 300 seconds
- bupa | trees=10 | selector=random_node | budget=20000 | stopped after 300 seconds
- bupa | trees=10 | selector=shapley | budget=20000 | stopped after 300 seconds
- bupa | trees=5 | selector=shapley | budget=20000 | stopped after 300 seconds
- ecoli | trees=10 | selector=info_gain | budget=20000 | stopped after 300 seconds
- ecoli | trees=10 | selector=modal | budget=20000 | stopped after 300 seconds
- ecoli | trees=10 | selector=p_value | budget=20000 | stopped after 300 seconds
- ecoli | trees=10 | selector=random_node | budget=20000 | stopped after 300 seconds
- ecoli | trees=10 | selector=shapley | budget=20000 | stopped after 300 seconds
- heart-c | trees=10 | selector=info_gain | budget=20000 | stopped after 300 seconds
- heart-c | trees=10 | selector=modal | budget=20000 | stopped after 300 seconds
- heart-c | trees=10 | selector=p_value | budget=20000 | stopped after 300 seconds
- heart-c | trees=10 | selector=random_node | budget=20000 | stopped after 300 seconds
- heart-c | trees=10 | selector=shapley | budget=20000 | stopped after 300 seconds
- heart-sa | trees=10 | selector=info_gain | budget=20000 | stopped after 300 seconds
- heart-sa | trees=10 | selector=modal | budget=20000 | stopped after 300 seconds
- heart-sa | trees=10 | selector=p_value | budget=20000 | stopped after 300 seconds
- heart-sa | trees=10 | selector=random_node | budget=20000 | stopped after 300 seconds
- heart-sa | trees=10 | selector=shapley | budget=20000 | stopped after 300 seconds
- seismic_bumps | trees=10 | selector=random_node | budget=20000 | stopped after 300 seconds
- seismic_bumps | trees=10 | selector=shapley | budget=20000 | stopped after 300 seconds

## Output Files

- `ALL_SUMMARIES.csv`: successful construction summaries
- `ALL_RANKINGS.csv`: variable rankings for successful runs
- `ALL_ROBUSTNESS.csv`: robustness rows if robustness samples were enabled
- `RUN_STATUS_ALL.csv`: one status row per attempted run
- `FAILURES.csv`: timeout/failure details
- each run folder contains `run.log`, and failed/timeout runs contain `error.txt`
