#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# Path to mpremote in the venv
$mpremote = Join-Path $PSScriptRoot "venv\Scripts\mpremote.exe"
if (-not (Test-Path $mpremote)) {
    Write-Error "mpremote not found at $mpremote. Activate venv or install mpremote in the project's venv."
    exit 1
}

# Parse arguments: accept optional port and optional 'noreboot' flag.
$noreboot = $false
$port = $null
foreach ($a in $args) {
    if ($a -ieq 'noreboot' -or $a -ieq '--noreboot' -or $a -ieq '-n') {
        $noreboot = $true
        continue
    }
    # treat any other argument as the port (e.g. COM3)
    if (-not $port) { $port = $a }
}
if (-not $port) { $port = 'COM3' }

# Copy files and directories to the device (creates dirs automatically)
Write-Output "Uploading to $port..."
& $mpremote connect $port fs cp -r boot.py main.py settings.py lib/ www/ :

# Soft-restart the device so new code runs (unless user requested no reboot)
if (-not $noreboot) {
    Write-Output "Rebooting device..."
    & $mpremote connect $port exec "import machine; machine.reset()"
} else {
    Write-Output "Upload complete (no reboot requested)."
}
