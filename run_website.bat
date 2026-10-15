@echo off
title Dinajpur Education Board Result Portal
cd /d "%~dp0"

echo =======================================================
echo   Dinajpur Education Board Result Portal (2015-2026)
echo   Developer: ShaifulXRD (Telegram: @ShaifulXD)
echo =======================================================
echo.
echo [*] Checking existing processes on Port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo [*] Stopping previous instance (PID: %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

timeout /t 1 /nobreak >nul
echo [*] Starting Website Server on http://127.0.0.1:5000 ...
start http://127.0.0.1:5000

python app.py
pause
