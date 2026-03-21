@echo off
setlocal

cd /d "%~dp0\..\..\apps\api"

:restart
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
echo [%date% %time%] API server exited. Restarting in 2 seconds...
timeout /t 2 /nobreak >nul
goto restart
