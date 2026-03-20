# Windows Docker Troubleshooting

## Current machine status

This repository has already been validated locally without Docker on this machine:

- `Node.js 24.14.0` installed
- `Python 3.11.9` installed
- Backend tests passed
- ML tests passed
- Frontend `build`, `lint`, and `typecheck` passed
- Live HTTP checks for the API and Next.js app returned `200`

The remaining blocker is Windows-level Docker setup:

- `docker` is not installed yet
- `wsl --status` reports that WSL is not installed
- `DISM` feature checks require an elevated PowerShell session
- Docker Desktop installation triggers an administrator prompt

## Fastest recovery path

Open **PowerShell as Administrator** and run:

```powershell
Set-Location C:\Users\yeojs\OneDrive\문서\news
.\infra\scripts\windows-enable-docker-prereqs.ps1 -InstallDockerDesktop
```

Then reboot Windows.

If the script reports that a reboot is required, that is expected on the first pass after enabling Windows features. Reboot once, then run the same command again.

After reboot, confirm the machine state:

```powershell
Set-Location C:\Users\yeojs\OneDrive\문서\news
wsl --status
.\infra\scripts\windows-preflight.ps1
```

If the preflight output is clean, start the full stack:

```powershell
.\infra\scripts\dev.ps1
```

## What the scripts do

- `infra/scripts/windows-preflight.ps1`
  - checks administrator status
  - checks `node`, `python`, `docker`, and `wsl`
  - checks whether `.env` exists
  - stops `dev.ps1` early when Docker prerequisites are missing
- `infra/scripts/windows-enable-docker-prereqs.ps1`
  - enables `Microsoft-Windows-Subsystem-Linux`
  - enables `VirtualMachinePlatform`
  - exits cleanly when Windows asks for a reboot before continuing
  - runs `wsl --install --no-distribution`
  - optionally installs Docker Desktop with `winget`
- `infra/scripts/dev.ps1`
  - runs the Windows preflight check first
  - launches `docker compose -f infra/docker-compose.yml up --build` only when prerequisites are satisfied

## Manual fallback

If Docker Desktop still fails after reboot:

1. Launch an elevated PowerShell session.
2. Run `wsl --status`.
3. If WSL is still unavailable, run:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

4. Reboot again.
5. Install Docker Desktop manually from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/).

## When Docker is ready

The expected local URLs are:

- Web: [http://localhost:3000](http://localhost:3000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- API health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
