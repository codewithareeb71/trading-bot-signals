$ErrorActionPreference = "Stop"
$activatePath = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-Not (Test-Path $activatePath)) {
    Write-Error "Virtual environment not found. Create it first with: python -m venv .venv"
    exit 1
}
& $activatePath
python main.py
