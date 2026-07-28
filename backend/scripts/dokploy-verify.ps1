#Requires -Version 5.1
<#
.SYNOPSIS
  Verify Momentra API + Celery readiness via Traefik Host header or public HTTPS.
#>
param(
  [string]$HostName = "api.mallaapp.org",
  [string]$TraefikBase = "http://192.168.68.108:80",
  [switch]$PublicOnly
)

$ErrorActionPreference = "Continue"

function Probe([string]$Url, [hashtable]$Headers = @{}) {
  try {
    $r = Invoke-WebRequest -Uri $Url -Headers $Headers -UseBasicParsing -TimeoutSec 20
    return @{ ok = $true; status = [int]$r.StatusCode; body = $r.Content }
  } catch {
    $code = $null
    if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    return @{ ok = $false; status = $code; body = $_.Exception.Message }
  }
}

Write-Host "=== public HTTPS ==="
$h = Probe "https://$HostName/health"
$ready = Probe "https://$HostName/health/ready"
Write-Host "/health      $($h.status) $($h.body)"
Write-Host "/health/ready $($ready.status) $($ready.body)"

if (-not $PublicOnly) {
  Write-Host "`n=== Traefik Host header ($TraefikBase) ==="
  $hdr = @{ Host = $HostName }
  $th = Probe "$TraefikBase/health" $hdr
  $tr = Probe "$TraefikBase/health/ready" $hdr
  Write-Host "/health      $($th.status) $($th.body)"
  Write-Host "/health/ready $($tr.status) $($tr.body)"
  $ready = $tr
}

$readyOk = $ready.body -match '"redis"\s*:\s*"up"' -and $ready.body -match '"celery"\s*:\s*"up"' -and $ready.body -match '"database"\s*:\s*"up"'
if ($readyOk) {
  Write-Host "`nPASS: database/redis/celery up"
  exit 0
}
Write-Host "`nFAIL: redis/celery not ready - deploy compose stack (api+worker+beat+redis). See DOKPLOY.md"
exit 1
