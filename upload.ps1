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

# NOTE: No hardware reset before upload intentionally.
# The device must already be at a quiet REPL (webserver stopped) before running this script.
# To stop the webserver from the REPL: WebServer().stop()
# A reboot is performed at the END to apply the new code (unless --noreboot is passed).

# Copy project files to device in a single mpremote session using chained commands.
Write-Output "Uploading to $port..."

# Build a single chained mpremote invocation: connect once, copy everything.
# mpremote supports chaining commands with '+' in a single session.
$cpArgs = [System.Collections.Generic.List[string]]::new()
$cpArgs.Add('connect')
$cpArgs.Add($port)

$first = $true
foreach ($f in (Get-ChildItem -Path $PSScriptRoot -Filter *.py)) {
    Write-Output "  $($f.Name)"
    if (-not $first) { $cpArgs.Add('+') }
    $cpArgs.AddRange([string[]]@('fs', 'cp', $f.FullName, ':'))
    $first = $false
}

if (Test-Path (Join-Path $PSScriptRoot 'lib')) {
    Write-Output "  lib/"
    $cpArgs.Add('+')
    $cpArgs.AddRange([string[]]@('fs', 'cp', '-r', (Join-Path $PSScriptRoot 'lib'), ':'))
}

if (Test-Path (Join-Path $PSScriptRoot 'www')) {
    Write-Output "  www/"
    $cpArgs.Add('+')
    $cpArgs.AddRange([string[]]@('fs', 'cp', '-r', (Join-Path $PSScriptRoot 'www'), ':'))
}

& $mpremote @cpArgs

# Optionally reboot after upload so new code runs immediately.
if (-not $noreboot) {
    Write-Output "Rebooting device..."
    & python "$PSScriptRoot\tools\reset_device.py" $port 2
} else {
    Write-Output "Upload complete (no reboot requested)."
}