@echo off
setlocal
cd /d "%~dp0"

title Antigravity Sound Setup

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ======================================================
    echo   ERROR: Python was not found!
    echo ======================================================
    echo Please install Python from https://www.python.org/
    echo and make sure to check:
    echo   "Add Python to PATH"
    echo during installation.
    echo.
    pause
    exit /b 1
)

python install.py %*

if %errorlevel% neq 0 (
    echo.
    echo [!] An error occurred during setup.
    echo.
) else (
    echo.
)

pause
