#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# Path to mpremote in the venv
$mpremote = Join-Path $PSScriptRoot "venv\Scripts\mpremote.exe"
if (-not (Test-Path $mpremote)) {
    Write-Error "mpremote not found at $mpremote. Run: pip install mpremote"
    exit 1
}

# Parse arguments: optional port, optional 'noreboot' flag.
$noreboot = $false
$port = $null
foreach ($a in $args) {
    if ($a -ieq 'noreboot' -or $a -ieq '--noreboot' -or $a -ieq '-n') {
        $noreboot = $true
        continue
    }
    if (-not $port) { $port = $a }
}
if (-not $port) { $port = 'COM3' }

# Hardware-reset via RTS pin -- no REPL needed, safe even when webserver is running.
Write-Output "Hardware resetting device on $port..."
& python "$PSScriptRoot\tools\reset_device.py" $port 2
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Reset script failed -- board may need manual reset."
}

# Copy project files to device.
Write-Output "Uploading to $port..."
& $mpremote connect $port fs cp -r boot.py main.py settings.py lib/ www/ :

# Optionally reboot after upload so new code runs immediately.
if (-not $noreboot) {
    Write-Output "Rebooting device..."
    & python "$PSScriptRoot\tools\reset_device.py" $port 2
} else {
    Write-Output "Upload complete (no reboot requested)."
}