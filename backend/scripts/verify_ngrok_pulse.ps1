# Verify Wedding pulse Bookings/Spent against the live ngrok API.
# Requires a logged-in Bearer token (browser Network tab) and moment id.
#
#   $env:MOMENTRA_API_BASE = "https://veggie-handmade-splashed.ngrok-free.dev"
#   $env:MOMENTRA_BEARER_TOKEN = "<token>"
#   $env:MOMENTRA_MOMENT_ID = "<uuid>"
#   powershell -File .\verify_ngrok_pulse.ps1
#
# Optional: set MOMENTRA_PROBE_BOOKING=1 to POST a probe booking then re-read pulse.

param(
    [switch]$ProbeBooking
)

$ErrorActionPreference = "Stop"
$base = $env:MOMENTRA_API_BASE
if (-not $base) { $base = "https://veggie-handmade-splashed.ngrok-free.dev" }
$token = $env:MOMENTRA_BEARER_TOKEN
$momentId = $env:MOMENTRA_MOMENT_ID
if (-not $token) { throw "Set MOMENTRA_BEARER_TOKEN" }
if (-not $momentId) { throw "Set MOMENTRA_MOMENT_ID" }
if ($env:MOMENTRA_PROBE_BOOKING -eq "1") { $ProbeBooking = $true }

$headers = @{
    Authorization = "Bearer $token"
    "ngrok-skip-browser-warning" = "1"
    "Content-Type" = "application/json"
}

function Get-Json([string]$Url) {
    $r = Invoke-WebRequest -Uri $Url -Headers $headers -UseBasicParsing -TimeoutSec 30
    return ($r.Content | ConvertFrom-Json)
}

Write-Host "Health..."
$health = Get-Json "$base/health"
Write-Host "  $($health | ConvertTo-Json -Compress)"

if ($ProbeBooking) {
    Write-Host "POST probe booking..."
    $body = @{
        booking_type = "flight"
        provider = "Air India Probe"
        title = "Air India Probe"
        booking_status = "confirmed"
        amount_minor = 1500000
    } | ConvertTo-Json
    $null = Invoke-WebRequest -Uri "$base/api/v1/group/trips/$momentId/quick-add/booking" `
        -Method POST -Headers $headers -Body $body -UseBasicParsing -TimeoutSec 30
    Write-Host "  created"
}

Write-Host "GET pulse?force_refresh=true..."
$pulse = Get-Json "$base/api/v1/group/trips/$momentId/pulse?force_refresh=true"
$bookings = [int64]$pulse.stats.confirmed_bookings
$spent = [int64]$pulse.stats.total_expenses_minor
$budget = [int64]$pulse.stats.total_budget_minor
$plans = [int64]$pulse.stats.active_plan_items
$recent = @()
if ($pulse.dashboard_card -and $pulse.dashboard_card.recent_items) {
    $recent = @($pulse.dashboard_card.recent_items)
}
Write-Host "  trip_name=$($pulse.trip_name)"
Write-Host "  confirmed_bookings=$bookings"
Write-Host "  active_plan_items=$plans"
Write-Host "  total_budget_minor=$budget"
Write-Host "  total_expenses_minor=$spent"
Write-Host "  recent_items=$($recent.Count)"
foreach ($item in $recent | Select-Object -First 8) {
    Write-Host "    - [$($item.activity_type)] $($item.title)"
}
if ($pulse.dashboard_card -and $pulse.dashboard_card.kpis) {
    foreach ($k in @($pulse.dashboard_card.kpis)) {
        Write-Host "  kpi $($k.kpi_id)=$($k.value)"
    }
}

Write-Host "GET activity..."
try {
    $activity = Get-Json "$base/api/v1/group/trips/$momentId/activity"
    $items = @($activity.items)
    $bookingActs = @($items | Where-Object { $_.activity_type -eq "BOOKING" })
    Write-Host "  activity_total=$($items.Count) booking_type=$($bookingActs.Count)"
} catch {
    Write-Host "  activity endpoint failed: $($_.Exception.Message)"
}

$ok = ($bookings -gt 0) -or ($spent -gt 0)
if (-not $ok -and $recent.Count -gt 0) {
    Write-Host ""
    Write-Host "FAIL - recent activity present but Bookings/Spent still 0. KPI fix not loaded on remote."
    exit 1
}
if (-not $ok) {
    Write-Host ""
    Write-Host "WARN - KPIs still 0 and no recent items. Store may have no bookings/expenses; try -ProbeBooking."
    exit 2
}

Write-Host ""
Write-Host "PASS - pulse KPIs non-zero (bookings=$bookings spent_minor=$spent)"
exit 0
