@echo off
title DocuSense AI — Desktop App
echo.
echo  ============================================================
echo    DocuSense AI - Contract & Policy Analyzer
echo    Team 2 - SRM IST Hack ^& Fest 2026
echo  ============================================================
echo.
echo  [*] Launching DocuSense AI Desktop App...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Change to the script directory
cd /d "%~dp0"

REM Run the desktop launcher
python desktop_app.py

echo.
echo  [*] DocuSense AI has been closed.
pause
