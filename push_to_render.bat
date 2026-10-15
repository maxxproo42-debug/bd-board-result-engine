@echo off
title Auto Deploy to Render (bd-board-result-engine)
color 0B
echo ================================================================
echo    BD BOARD RESULT ENGINE - AUTO DEPLOY TO GITHUB & RENDER
echo ================================================================
echo.

cd /d "%~dp0"

REM Ensure MinGit is on PATH
set "PATH=%~dp0..\mingit\cmd;%~dp0..\mingit\mingw64\bin;%PATH%"

echo [1/3] Checking Git Status and Staging all updates...
git add -A

echo.
echo [2/3] Creating Auto-Commit...
git commit -m "Auto deploy update to Render [%date% %time%]"

echo.
echo [3/3] Pushing to GitHub (https://github.com/maxxproo42-debug/bd-board-result-engine)...
echo (Note: If prompted in browser, click 'Authorize' to grant 1-time access)
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo    SUCCESS! Code pushed to GitHub 'main' branch successfully!
    echo    Render is now automatically building & deploying your app!
    echo    Live site: https://bd-board-result-engine-1.onrender.com/
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo    [!] Push failed or waiting for authentication.
    echo    If browser opened, complete the login and run this again.
    echo ================================================================
)

echo.
echo Press any key to exit...
pause >nul
