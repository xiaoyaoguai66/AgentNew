Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPython = Join-Path $repoRoot "backend\.venv\Scripts\python.exe"

function Invoke-CheckedCommand {
    param(
        [string]$Step,
        [scriptblock]$Command
    )

    Write-Host $Step
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Step (exit code $LASTEXITCODE)"
    }
}

if (-not (Test-Path $backendPython)) {
    throw "Backend virtualenv python not found: $backendPython"
}

Invoke-CheckedCommand "[1/4] Backend targeted compile checks" {
    & $backendPython (Join-Path $repoRoot "backend\tests\check_backend_compile.py")
}

Push-Location (Join-Path $repoRoot "backend")
try {
    Invoke-CheckedCommand "[2/4] Backend smoke checks" {
        & $backendPython "tests\smoke_api.py"
    }

    Invoke-CheckedCommand "[3/4] Backend integration checks" {
        & $backendPython "tests\integration_api.py"
    }
}
finally {
    Pop-Location
}

Push-Location (Join-Path $repoRoot "frontend")
try {
    Invoke-CheckedCommand "[4/4] Frontend build" {
        & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Command "npm.cmd run build"
    }
}
finally {
    Pop-Location
}

Write-Host "NewsCopilot dev-check passed."

