[CmdletBinding()]
param(
    [switch]$RequireDocker,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

function Write-Check {
    param(
        [string]$State,
        [string]$Name,
        [string]$Detail
    )

    if ($Quiet) {
        return
    }

    $color = switch ($State) {
        "OK" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        default { "White" }
    }

    Write-Host ("[{0}] {1} - {2}" -f $State, $Name, $Detail) -ForegroundColor $color
}

function Add-Check {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$State,
        [string]$Name,
        [string]$Detail
    )

    $check = [pscustomobject]@{
        State  = $State
        Name   = $Name
        Detail = $Detail
    }

    $Checks.Add($check) | Out-Null
    Write-Check -State $State -Name $Name -Detail $Detail
}

function Get-CommandText {
    param(
        [string]$CommandName,
        [string[]]$Arguments
    )

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if (-not $command) {
        return $null
    }

    try {
        $output = & $CommandName @Arguments 2>&1 | Out-String
        return $output.Trim()
    }
    catch {
        return $null
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$checks = [System.Collections.Generic.List[object]]::new()

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Add-Check -Checks $checks -State "OK" -Name "Administrator session" -Detail "Elevated PowerShell session detected."
}
else {
    Add-Check -Checks $checks -State "WARN" -Name "Administrator session" -Detail "This shell is not elevated. WSL feature activation and Docker Desktop install will require Run as administrator."
}

$nodeVersion = Get-CommandText -CommandName "node" -Arguments @("-v")
if ($nodeVersion) {
    Add-Check -Checks $checks -State "OK" -Name "Node.js" -Detail $nodeVersion
}
else {
    Add-Check -Checks $checks -State "FAIL" -Name "Node.js" -Detail "node was not found in PATH."
}

$pythonVersion = Get-CommandText -CommandName "py" -Arguments @("-V")
if (-not $pythonVersion) {
    $pythonVersion = Get-CommandText -CommandName "python" -Arguments @("--version")
}

if ($pythonVersion) {
    Add-Check -Checks $checks -State "OK" -Name "Python" -Detail $pythonVersion
}
else {
    Add-Check -Checks $checks -State "FAIL" -Name "Python" -Detail "Python launcher was not found in PATH."
}

$envFile = Join-Path $repoRoot ".env"
if (Test-Path $envFile) {
    Add-Check -Checks $checks -State "OK" -Name "Root env file" -Detail ".env is present."
}
else {
    Add-Check -Checks $checks -State "WARN" -Name "Root env file" -Detail ".env is missing. Copy .env.example to .env before first run."
}

$dockerVersion = Get-CommandText -CommandName "docker" -Arguments @("--version")
$dockerCliFallback = Join-Path $env:ProgramFiles "Docker\Docker\resources\bin\docker.exe"
$dockerDesktopCandidates = @(
    (Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"),
    (Join-Path $env:LocalAppData "Programs\Docker\Docker\Docker Desktop.exe")
) | Where-Object { $_ -and (Test-Path $_) }

if ($dockerVersion) {
    Add-Check -Checks $checks -State "OK" -Name "Docker CLI" -Detail $dockerVersion
}
elseif (Test-Path $dockerCliFallback) {
    try {
        $dockerVersion = (& $dockerCliFallback --version 2>&1 | Out-String).Trim()
        $dockerBin = Split-Path $dockerCliFallback -Parent
        if (-not (($env:Path -split ";") -contains $dockerBin)) {
            $env:Path = $dockerBin + ";" + $env:Path
        }
        Add-Check -Checks $checks -State "OK" -Name "Docker CLI" -Detail ($dockerVersion + " (via Docker Desktop install)")
    }
    catch {
        Add-Check -Checks $checks -State "WARN" -Name "Docker CLI" -Detail "Docker Desktop binaries exist, but docker.exe could not be executed."
    }
}
elseif ($dockerDesktopCandidates.Count -gt 0) {
    Add-Check -Checks $checks -State "WARN" -Name "Docker Desktop" -Detail ("Docker Desktop binaries exist at {0}, but docker is not yet available in PATH." -f $dockerDesktopCandidates[0])
}
elseif ($RequireDocker) {
    Add-Check -Checks $checks -State "FAIL" -Name "Docker CLI" -Detail "docker was not found. Install Docker Desktop after enabling WSL2."
}
else {
    Add-Check -Checks $checks -State "WARN" -Name "Docker CLI" -Detail "docker was not found."
}

$wslStatus = Get-CommandText -CommandName "wsl" -Arguments @("--status")
if ($wslStatus) {
    Add-Check -Checks $checks -State "OK" -Name "WSL" -Detail "WSL command is available."
}
else {
    Add-Check -Checks $checks -State "FAIL" -Name "WSL" -Detail "WSL is not installed or not initialized. Run infra/scripts/windows-enable-docker-prereqs.ps1 as Administrator, then reboot."
}

if ($isAdmin) {
    try {
        $wslFeature = & dism.exe /online /Get-FeatureInfo /FeatureName:Microsoft-Windows-Subsystem-Linux 2>&1 | Out-String
        if ($wslFeature -match "State : Enabled") {
            Add-Check -Checks $checks -State "OK" -Name "Windows feature: WSL" -Detail "Microsoft-Windows-Subsystem-Linux is enabled."
        }
        else {
            Add-Check -Checks $checks -State "WARN" -Name "Windows feature: WSL" -Detail "Microsoft-Windows-Subsystem-Linux is not enabled."
        }
    }
    catch {
        Add-Check -Checks $checks -State "WARN" -Name "Windows feature: WSL" -Detail "Unable to inspect WSL optional feature."
    }

    try {
        $vmFeature = & dism.exe /online /Get-FeatureInfo /FeatureName:VirtualMachinePlatform 2>&1 | Out-String
        if ($vmFeature -match "State : Enabled") {
            Add-Check -Checks $checks -State "OK" -Name "Windows feature: VirtualMachinePlatform" -Detail "VirtualMachinePlatform is enabled."
        }
        else {
            Add-Check -Checks $checks -State "WARN" -Name "Windows feature: VirtualMachinePlatform" -Detail "VirtualMachinePlatform is not enabled."
        }
    }
    catch {
        Add-Check -Checks $checks -State "WARN" -Name "Windows feature: VirtualMachinePlatform" -Detail "Unable to inspect VirtualMachinePlatform optional feature."
    }
}
else {
    Add-Check -Checks $checks -State "WARN" -Name "Windows optional features" -Detail "Detailed WSL feature checks were skipped because this shell is not elevated."
}

$rebootPendingKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending"
if (Test-Path $rebootPendingKey) {
    Add-Check -Checks $checks -State "WARN" -Name "Pending reboot" -Detail "Windows reports a pending reboot. Reboot before retrying Docker setup."
}

$failedChecks = @($checks | Where-Object { $_.State -eq "FAIL" })
$warningChecks = @($checks | Where-Object { $_.State -eq "WARN" })

if (-not $Quiet) {
    Write-Host ""
    Write-Host ("Summary: {0} failed, {1} warning(s)." -f $failedChecks.Count, $warningChecks.Count)
}

if ($failedChecks.Count -gt 0) {
    exit 1
}

exit 0
