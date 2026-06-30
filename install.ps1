<#
.SYNOPSIS
    Install jsony-reader to the user's scripts directory.
    Idempotent: safe to re-run. Requires Python 3 (stdlib only).

.DESCRIPTION
    Copies jsony_core.py and jsony-reader to $DEST and creates a
    jsony-reader.cmd batch wrapper so the tool is callable from any
    Command Prompt or PowerShell session (if DEST is on PATH).

    Default destination: $env:USERPROFILE\.claude\scripts\jsony-reader

.PARAMETER Dest
    Custom installation directory (optional).

.EXAMPLE
    .\install.ps1
    .\install.ps1 C:\tools\jsony-reader
#>

param(
    [string]$Dest = "$env:USERPROFILE\.claude\scripts\jsony-reader"
)

$ErrorActionPreference = "Stop"

# Resolve the directory where this script lives
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check Python 3
$python = $null
foreach ($cmd in @("python3", "python")) {
    try {
        $v = & $cmd --version 2>&1
        if ($v -match "Python 3") {
            $python = $cmd
            break
        }
    } catch {}
}
if (-not $python) {
    Write-Error "Python 3 is required but not found on PATH. Install Python 3 first."
    exit 1
}
Write-Host "[ok] found $python"

# Create destination
if (-not (Test-Path $Dest)) {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
}
Write-Host "[ok] destination: $Dest"

# Copy files
Copy-Item -Path (Join-Path $Src "jsony_core.py") -Destination (Join-Path $Dest "jsony_core.py") -Force
Copy-Item -Path (Join-Path $Src "jsony-reader") -Destination (Join-Path $Dest "jsony-reader") -Force
Write-Host "[ok] copied jsony_core.py + jsony-reader"

# Create a .cmd batch wrapper so 'jsony-reader' works from any prompt
$CmdPath = Join-Path $Dest "jsony-reader.cmd"
@"
@echo off
python "%~dp0jsony-reader" %*
"@ | Set-Content -Path $CmdPath -Encoding ASCII
Write-Host "[ok] created wrapper: $CmdPath"

# Optional: suggest adding to PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$Dest*") {
    Write-Host ""
    Write-Host "[!] $Dest is NOT on your PATH."
    Write-Host "    To add it, run this command (as administrator for system-wide):"
    Write-Host ""
    Write-Host "    [Environment]::SetEnvironmentVariable(`"Path`", `"`$env:Path;$Dest`", `"User`")"
    Write-Host ""
    Write-Host "    Or just reopen your terminal after adding it manually."
}

# Self-check
Write-Host ""
Write-Host "--- self-check ---"
$check = & $python (Join-Path $Dest "jsony-reader") "--help" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[ok] jsony-reader --help passed"
} else {
    Write-Warning "self-check failed. Output:"
    Write-Warning $check
}

Write-Host ""
Write-Host "installed jsony-reader -> $Dest"
