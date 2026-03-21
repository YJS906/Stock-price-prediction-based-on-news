@echo off
setlocal

cd /d "%~dp0\..\..\apps\web"
set "PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VisualStudio\NodeJs;%PATH%"

:restart
call "..\..\node_modules\.bin\next.cmd" dev --hostname 0.0.0.0 --port 3000
echo [%date% %time%] Web server exited. Restarting in 2 seconds...
timeout /t 2 /nobreak >nul
goto restart
