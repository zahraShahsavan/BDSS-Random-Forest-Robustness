$ErrorActionPreference = "Stop"

Write-Host "Running BDSS full experiment grid..."
Write-Host "This runs 54 datasets x 2 tree counts x 2 fast selectors = 216 runs."
Write-Host "Each run has a 10-minute timeout, so one hard dataset cannot block the full grid."
Write-Host "This first pass skips robustness samples to focus on construction records."
Write-Host ""

$PythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
  $PythonExe = "py"
}

& $PythonExe .\scripts\run_all_54_experiments.py `
  --datasets datasets `
  --out results\full_54_grid `
  --budget 20000 `
  --max-test-samples 10 `
  --timeout-seconds 300 `
  --selectors modal,random_node

Write-Host ""
Write-Host "Done. Open these files:"
Write-Host "  results\full_54_grid\EXPERIMENT_REPORT.md"
Write-Host "  results\full_54_grid\RUN_STATUS_ALL.csv"
Write-Host "  results\full_54_grid\ALL_SUMMARIES.csv"
Write-Host "  results\full_54_grid\FAILURES.csv"
