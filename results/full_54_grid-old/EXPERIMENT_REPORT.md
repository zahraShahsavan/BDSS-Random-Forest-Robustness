# BDSS Experiment Report

This report is generated automatically by `scripts/run_all_54_experiments.py`.

## Summary

- Total recorded runs: 108
- Completed or already completed: 44
- Timed out: 64
- Failed: 0
- Skipped on resume: 38

A timeout means the run exceeded the configured threshold, was stopped, recorded, and the script continued to the next dataset/tree/selector combination.

## Timed Out Runs

- ann-thyroid | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- ann-thyroid | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- biodegradation | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- biodegradation | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- breast-cancer-wisconsin | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- breast-cancer-wisconsin | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- cloud | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- diabetes | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- factors | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- factors | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- fourier | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- fourier | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- glass | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- glass | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- ionosphere | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- ionosphere | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- karhunen | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- karhunen | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- letter | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- letter | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- magic | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- magic | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- messidor | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- messidor | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- pendigits | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- pendigits | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- phoneme | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- phoneme | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- pima | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- pima | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- ring | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- ring | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- segmentation | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- segmentation | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- shuttle | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- shuttle | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- sonar | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- sonar | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- spambase | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- spambase | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- spectf | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- texture | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- texture | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- twonorm | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- twonorm | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- vehicle | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- vehicle | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- vowel | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- vowel | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- waveform-21 | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- waveform-21 | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- waveform-40 | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- waveform-40 | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- wdbc | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- wdbc | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- wine-quality-red | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- wine-quality-red | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- wine-quality-white | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- wine-quality-white | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds
- wine-recog | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- wine-recognition | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- wpbc | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- zernike | trees=10 | selector=modal | budget=20000 | stopped after 600 seconds
- zernike | trees=5 | selector=modal | budget=20000 | stopped after 600 seconds

## Output Files

- `ALL_SUMMARIES.csv`: successful construction summaries
- `ALL_RANKINGS.csv`: variable rankings for successful runs
- `ALL_ROBUSTNESS.csv`: robustness rows if robustness samples were enabled
- `RUN_STATUS_ALL.csv`: one status row per attempted run
- `FAILURES.csv`: timeout/failure details
- each run folder contains `run.log`, and failed/timeout runs contain `error.txt`
