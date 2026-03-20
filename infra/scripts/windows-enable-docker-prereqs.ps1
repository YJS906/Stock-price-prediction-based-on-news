[CmdletBinding()]
param(
    [switch]$InstallDockerDesktop,
    [string]$LogPath
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if (-not $LogPath) {
    $LogPath = Join-Path $repoRoot "docs\windows-enable-run.log"
}

$transcriptStarted = $false
try {
    Start-Transcript -Path $LogPath -Force | Out-Null
    $transcriptStarted = $true
}
catch {
    Write-Warning "Transcript logging could not be started."
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$restartRequired = $false

if (-not $isAdmin) {
    if ($transcriptStarted) {
        Stop-Transcript | Out-Null
    }
    Write-Error "Run this script from an elevated PowerShell session."
    exit 1
}

Write-Host "Enabling Windows Subsystem for Linux..." -ForegroundColor Cyan
& dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
if ($LASTEXITCODE -eq 3010) {
    $restartRequired = $true
}
elseif ($LASTEXITCODE -ne 0) {
    throw "Failed to enable Microsoft-Windows-Subsystem-Linux."
}

Write-Host "Enabling VirtualMachinePlatform..." -ForegroundColor Cyan
& dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
if ($LASTEXITCODE -eq 3010) {
    $restartRequired = $true
}
elseif ($LASTEXITCODE -ne 0) {
    throw "Failed to enable VirtualMachinePlatform."
}

if ($restartRequired) {
    Write-Host ""
    Write-Host "A reboot is required before WSL bootstrap and Docker Desktop installation can continue." -ForegroundColor Yellow
    Write-Host "Reboot Windows, then rerun this script." -ForegroundColor Yellow
    if ($transcriptStarted) {
        Stop-Transcript | Out-Null
    }
    exit 0
}

Write-Host "Bootstrapping WSL without installing a Linux distribution..." -ForegroundColor Cyan
try {
    & wsl.exe --install --no-distribution
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "wsl.exe returned a non-zero exit code. Reboot first and retry if WSL is still unavailable."
    }
}
catch {
    Write-Warning "wsl.exe could not complete bootstrap. Reboot first and then run `wsl --status`."
}

if ($InstallDockerDesktop) {
    Write-Host "Installing Docker Desktop with winget..." -ForegroundColor Cyan
    & winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Docker Desktop installer did not finish successfully. Reboot and run the installer again if needed."
    }
}

Write-Host ""
Write-Host "Windows features were updated. Reboot the machine before starting Docker Desktop." -ForegroundColor Green
Write-Host "After reboot:" -ForegroundColor Green
Write-Host "1. Run: wsl --status"
Write-Host "2. Install or launch Docker Desktop"
Write-Host "3. Run: .\\infra\\scripts\\dev.ps1"

if ($transcriptStarted) {
    Stop-Transcript | Out-Null
}
