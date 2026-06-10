@echo off
title Git Clone
color 0B

set SCRIPTDIR=%~dp0
set SCRIPTDIR=%SCRIPTDIR:~0,-1%

py --version >nul 2>&1
if %errorlevel% == 0 (
    py "%SCRIPTDIR%\git_clone.py"
    exit /b 0
)

python --version >nul 2>&1
if %errorlevel% == 0 (
    python "%SCRIPTDIR%\git_clone.py"
    exit /b 0
)

echo.
echo  [!] Python not found. Run setup.bat first.
echo.
pause
exit /b 1