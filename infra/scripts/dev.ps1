$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$preflightScript = Join-Path $PSScriptRoot "windows-preflight.ps1"
$dockerBin = Join-Path $env:ProgramFiles "Docker\Docker\resources\bin"

if (Test-Path $dockerBin -and -not (($env:Path -split ";") -contains $dockerBin)) {
    $env:Path = $dockerBin + ";" + $env:Path
}

& $preflightScript -RequireDocker
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Push-Location $repoRoot
try {
    docker compose -f infra/docker-compose.yml up --build
}
finally {
    Pop-Location
}
