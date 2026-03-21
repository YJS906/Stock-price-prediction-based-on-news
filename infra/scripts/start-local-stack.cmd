@echo off
setlocal

cd /d "%~dp0"
start "newsalpha-api" "%~dp0run-api-dev.cmd"
start "newsalpha-web" "%~dp0run-web-dev.cmd"
