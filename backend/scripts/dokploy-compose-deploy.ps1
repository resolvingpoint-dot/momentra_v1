#Requires -Version 5.1
<#
.SYNOPSIS
  Create/update a Dokploy Compose app for Momentra (api+worker+beat+redis) and deploy.

.NOTES
  Requires DOKPLOY_API_KEY from Dokploy → Settings → Profile → API/CLI.
  Defaults DOKPLOY_URL to http://192.168.68.108:3000
#>
param(
  [string]$DokployUrl = $env:DOKPLOY_URL,
  [string]$ApiKey = $env:DOKPLOY_API_KEY,
  [string]$ComposeName = $(if ($env:DOKPLOY_COMPOSE_NAME) { $env:DOKPLOY_COMPOSE_NAME } else { "momentra-backend" }),
  [string]$EnvFile = $(if ($env:DOKPLOY_ENV_FILE) { $env:DOKPLOY_ENV_FILE } else { "" }),
  [string]$DomainHost = $(if ($env:DOKPLOY_DOMAIN) { $env:DOKPLOY_DOMAIN } else { "api.mallaapp.org" }),
  [switch]$SkipDeploy
)

$ErrorActionPreference = "Stop"

if (-not $DokployUrl) { $DokployUrl = "http://192.168.68.108:3000" }
$DokployUrl = $DokployUrl.TrimEnd("/")

if (-not $ApiKey) {
  Write-Error "Set DOKPLOY_API_KEY (Dokploy → Settings → Profile → API/CLI)."
}

$BackendRoot = Split-Path -Parent $PSScriptRoot
$ComposePath = Join-Path $BackendRoot "docker-compose.yml"
if (-not (Test-Path $ComposePath)) {
  Write-Error "Missing compose file: $ComposePath"
}
$ComposeFile = Get-Content -Raw -Path $ComposePath

function Invoke-Dokploy {
  param(
    [ValidateSet("GET", "POST")][string]$Method,
    [string]$Path,
    [object]$Body = $null
  )
  $headers = @{
    "accept" = "application/json"
    "x-api-key" = $ApiKey
  }
  $uri = "$DokployUrl$Path"
  if ($null -ne $Body) {
    $json = $Body | ConvertTo-Json -Depth 20 -Compress
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType "application/json" -Body $json
  }
  return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

Write-Host "Dokploy: $DokployUrl"
Write-Host "Listing projects..."
$projects = Invoke-Dokploy -Method GET -Path "/api/project.all"
if (-not $projects -or $projects.Count -lt 1) {
  Write-Error "No projects found. Create a project in Dokploy UI first."
}

$project = $projects[0]
$environmentId = $null
if ($project.environments -and $project.environments.Count -gt 0) {
  $environmentId = $project.environments[0].environmentId
} elseif ($project.environmentId) {
  $environmentId = $project.environmentId
}

# Newer Dokploy nests compose under environments[]
$existing = $null
foreach ($p in $projects) {
  if ($p.compose) {
    foreach ($c in $p.compose) {
      if ($c.name -eq $ComposeName -or $c.appName -like "*$ComposeName*") { $existing = $c; break }
    }
  }
  if ($p.environments) {
    foreach ($env in $p.environments) {
      if (-not $environmentId) { $environmentId = $env.environmentId }
      if ($env.compose) {
        foreach ($c in $env.compose) {
          if ($c.name -eq $ComposeName -or $c.appName -like "*$ComposeName*") {
            $existing = $c
            $environmentId = $env.environmentId
            break
          }
        }
      }
    }
  }
  if ($existing) { break }
}

if (-not $environmentId) {
  Write-Error "Could not resolve environmentId from project.all. Create an environment in Dokploy UI."
}

Write-Host "Project: $($project.name)  environmentId=$environmentId"

$composeId = $null
if ($existing) {
  $composeId = $existing.composeId
  Write-Host "Updating existing compose $ComposeName ($composeId)"
  Invoke-Dokploy -Method POST -Path "/api/compose.update" -Body @{
    composeId = $composeId
    name = $ComposeName
    composeType = "docker-compose"
    sourceType = "raw"
    composeFile = $ComposeFile
    composePath = "./docker-compose.yml"
  } | Out-Null
} else {
  Write-Host "Creating compose $ComposeName"
  $created = Invoke-Dokploy -Method POST -Path "/api/compose.create" -Body @{
    name = $ComposeName
    environmentId = $environmentId
    composeType = "docker-compose"
    appName = ($ComposeName -replace "[^a-zA-Z0-9._-]", "-")
  }
  $composeId = $created.composeId
  if (-not $composeId) { $composeId = $created.id }
  if (-not $composeId) {
    Write-Error "compose.create did not return composeId: $($created | ConvertTo-Json -Depth 5)"
  }
  Invoke-Dokploy -Method POST -Path "/api/compose.update" -Body @{
    composeId = $composeId
    sourceType = "raw"
    composeFile = $ComposeFile
    composePath = "./docker-compose.yml"
  } | Out-Null
}

if ($EnvFile -and (Test-Path $EnvFile)) {
  Write-Host "Saving environment from $EnvFile (REDIS_URL forced in compose; stripping localhost Redis overrides)"
  $lines = Get-Content $EnvFile | Where-Object {
    $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' -and
    $_ -notmatch '^\s*REDIS_URL\s*=' -and
    $_ -notmatch '^\s*CELERY_BROKER_URL\s*=' -and
    $_ -notmatch '^\s*CELERY_RESULT_BACKEND\s*=' -and
    $_ -notmatch '^\s*ALLOW_TEST_AUTH\s*='
  }
  $envBody = ($lines -join "`n") + "`n"
  Invoke-Dokploy -Method POST -Path "/api/compose.saveEnvironment" -Body @{
    composeId = $composeId
    env = $envBody
  } | Out-Null
} else {
  Write-Host "No DOKPLOY_ENV_FILE — keeping existing Dokploy Environment (ensure DATABASE_URL + secrets are set in UI)."
}

# Domain (best-effort; schema varies by Dokploy version)
try {
  Write-Host "Ensuring domain $DomainHost → service api:8000"
  $one = Invoke-Dokploy -Method GET -Path "/api/compose.one?composeId=$composeId"
  $hasDomain = $false
  if ($one.domains) {
    foreach ($d in $one.domains) {
      if ($d.host -eq $DomainHost) { $hasDomain = $true }
    }
  }
  if (-not $hasDomain) {
    Invoke-Dokploy -Method POST -Path "/api/domain.create" -Body @{
      host = $DomainHost
      path = "/"
      port = 8000
      https = $false
      composeId = $composeId
      serviceName = "api"
    } | Out-Null
  }
} catch {
  Write-Warning "Domain API skipped (create domain in UI if needed): $($_.Exception.Message)"
}

if (-not $SkipDeploy) {
  Write-Host "Deploying compose $composeId ..."
  Invoke-Dokploy -Method POST -Path "/api/compose.deploy" -Body @{ composeId = $composeId } | Out-Null
  Write-Host "Deploy triggered. Watch Dokploy → Deployments / Logs for api, worker, beat, redis."
}

Write-Host "composeId=$composeId"
Write-Host "Verify: curl -H `"Host: $DomainHost`" http://127.0.0.1:80/health/ready"
