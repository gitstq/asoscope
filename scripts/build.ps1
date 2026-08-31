# Cross-platform build script for Windows PowerShell.
# Builds a wheel into dist\ using only pip — no third-party build tooling.
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "[build] interpreter:" (& $Python --version)
if ($LASTEXITCODE -ne 0) { Write-Error "python not found on PATH"; exit 1 }

Write-Host "[build] cleaning previous artifacts"
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
if (Test-Path build) { Remove-Item -Recurse -Force build }
Get-ChildItem -Filter *.egg-info -Directory | Remove-Item -Recurse -Force

Write-Host "[build] running test suite"
& $Python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { Write-Error "tests failed"; exit 1 }

Write-Host "[build] building wheel into dist\"
& $Python -m pip wheel . --no-deps -w dist
if ($LASTEXITCODE -ne 0) { Write-Error "wheel build failed"; exit 1 }

Get-ChildItem dist
Write-Host "[build] done. Install with: $Python -m pip install dist\asoscope_cli-*.whl"
