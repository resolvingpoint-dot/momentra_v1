param(
    [string]$BackendRoot = ""
)

$ErrorActionPreference = "Stop"
if (-not $BackendRoot) {
    $BackendRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
} else {
    $BackendRoot = (Resolve-Path $BackendRoot).Path
}

$checks = @(
    @{ Path = "app\domains\group\templates\shared_experience\pulse_mapper.py"; Needle = "confirmed_bookings=ctx.booking_count" },
    @{ Path = "app\domains\group\templates\shared_experience\projection_builder.py"; Needle = "orphan_timeline_bookings" },
    @{ Path = "app\domains\group\templates\shared_experience\projection_helpers.py"; Needle = "def booking_status" },
    @{ Path = "app\domains\group\projection_read.py"; Needle = "stale-rebuild" },
    @{ Path = "app\domains\group\trip_deep_service.py"; Needle = '"status": booking_status' }
)

Write-Host "Fingerprinting: $BackendRoot"
$failed = New-Object System.Collections.Generic.List[string]
foreach ($c in $checks) {
    $full = Join-Path $BackendRoot $c.Path
    if (-not (Test-Path $full)) {
        [void]$failed.Add("MISSING FILE: $($c.Path)")
        continue
    }
    $text = Get-Content -Raw -LiteralPath $full
    if ($text -notmatch [regex]::Escape($c.Needle)) {
        [void]$failed.Add("MISSING MARKER in $($c.Path): $($c.Needle)")
    } else {
        Write-Host "OK  $($c.Path)"
    }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "FAIL - backend missing KPI fix:"
    foreach ($f in $failed) { Write-Host "  $f" }
    exit 1
}

Write-Host ""
Write-Host "PASS - pulse KPI fix markers present"
exit 0
