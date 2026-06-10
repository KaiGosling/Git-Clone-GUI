@echo off
title Git Clone - Setup
color 0B
echo.
echo  ============================================
echo   GIT CLONE - Setup Installer
echo  ============================================
echo.

set SCRIPTDIR=%~dp0
set SCRIPTDIR=%SCRIPTDIR:~0,-1%

:: ── Find Python ──────────────────────────────────────────────────────────────
echo  [1/6] Looking for Python...

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYCMD=py
    for /f "tokens=*" %%i in ('py --version') do set PYVER=%%i
    echo       Found: %PYVER%
    goto :pip
)

python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYCMD=python
    for /f "tokens=*" %%i in ('python --version') do set PYVER=%%i
    echo       Found: %PYVER%
    goto :pip
)

echo.
echo  [!] Python not found on this PC.
echo      Please install Python first: https://www.python.org/downloads/
echo      During install, tick "Add Python to PATH"
echo.
pause
start https://www.python.org/downloads/
exit /b 1

:: ── Upgrade pip ──────────────────────────────────────────────────────────────
:pip
echo.
echo  [2/6] Upgrading pip...
%PYCMD% -m pip install --upgrade pip --quiet
echo       Done.

:: ── Check git ────────────────────────────────────────────────────────────────
echo.
echo  [3/6] Checking for git...
git --version >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=*" %%i in ('git --version') do set GITVER=%%i
    echo       Found: %GITVER%
) else (
    echo.
    echo  [!] git is not installed or not in PATH.
    echo      Download from: https://git-scm.com/download/win
    echo      During install, choose "Git from the command line and also from 3rd-party software"
    echo.
    choice /C YN /M "  Open git download page now?"
    if %errorlevel% == 1 (
        start https://git-scm.com/download/win
    )
    echo.
    echo      Re-run this setup after installing git.
    echo.
    pause
    exit /b 1
)

:: ── Install Python packages ───────────────────────────────────────────────────
echo.
echo  [4/6] Checking Python packages...
echo.

%PYCMD% -c "import tkinter" >nul 2>&1
if %errorlevel% == 0 (
    echo       tkinter  - already available.
) else (
    echo  [!] tkinter not found. Reinstall Python and check "tcl/tk and IDLE" during setup.
    pause
    exit /b 1
)

call :ensure pillow  Pillow

:: ── Install PyInstaller ──────────────────────────────────────────────────────
echo.
echo  [5/6] Installing PyInstaller...
%PYCMD% -m pip install pyinstaller --quiet
echo       Done.

:: ── Build EXE ────────────────────────────────────────────────────────────────
echo.
echo  [6/6] Building Git Clone.exe ...
echo       This may take a minute, please wait...
echo.

:: Remove old EXE and build cache for a clean compile
if exist "%SCRIPTDIR%\Git Clone.exe" (
    echo       Removing old Git Clone.exe...
    del /f /q "%SCRIPTDIR%\Git Clone.exe"
)
if exist "%SCRIPTDIR%\build" (
    rmdir /s /q "%SCRIPTDIR%\build"
)

:: Convert icon.png -> icon.ico if .ico doesn't exist yet
if not exist "%SCRIPTDIR%\assets\icon.ico" (
    if exist "%SCRIPTDIR%\assets\icon.png" (
        echo       Converting icon.png to icon.ico...
        %PYCMD% -c "from PIL import Image; img=Image.open(r'%SCRIPTDIR%\assets\icon.png'); img.save(r'%SCRIPTDIR%\assets\icon.ico')"
    )
)

:: Locate pyinstaller.exe dynamically
for /f "delims=" %%P in ('%PYCMD% -c "import sys,os; print(os.path.join(sys.prefix, chr(83)+chr(99)+chr(114)+chr(105)+chr(112)+chr(116)+chr(115), chr(112)+chr(121)+chr(105)+chr(110)+chr(115)+chr(116)+chr(97)+chr(108)+chr(108)+chr(101)+chr(114)+chr(46)+chr(101)+chr(120)+chr(101)))"') do set PYINST=%%P

if not exist "%PYINST%" (
    set PYINST=%LOCALAPPDATA%\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe
)

if not exist "%PYINST%" (
    echo  [!] Could not find pyinstaller.exe — skipping EXE build.
    echo      You can still run:  py git_clone.py
    goto :done
)

"%PYINST%" ^
    --noconsole ^
    --onefile ^
    --name "Git Clone" ^
    --icon="%SCRIPTDIR%\assets\icon.ico" ^
    --add-data "%SCRIPTDIR%\assets;assets" ^
    --distpath "%SCRIPTDIR%" ^
    --workpath "%SCRIPTDIR%\build" ^
    --specpath "%SCRIPTDIR%" ^
    "%SCRIPTDIR%\git_clone.py"

if %errorlevel% neq 0 (
    echo.
    echo  [!] EXE build failed. You can still run:  py git_clone.py
    goto :done
)
echo.
echo       Git Clone.exe built successfully!
echo       Location: %SCRIPTDIR%\Git Clone.exe

:: ── Done ─────────────────────────────────────────────────────────────────────
:done
echo.
echo  ============================================
echo   Setup complete!
echo  ============================================
echo.
echo   Python      - OK
echo   git         - OK
echo   tkinter     - OK
echo   Pillow      - image processing
echo   PyInstaller - app compiler
echo.
echo   EXE location:  Git Clone.exe  (same folder)
echo   Or run directly:  py git_clone.py
echo.
pause

choice /C YN /M "  Launch Git Clone now?"
if %errorlevel% == 1 (
    if exist "%SCRIPTDIR%\Git Clone.exe" (
        start "" "%SCRIPTDIR%\Git Clone.exe"
    ) else (
        %PYCMD% "%SCRIPTDIR%\git_clone.py"
    )
)
exit /b 0

:: ── Subroutine ───────────────────────────────────────────────────────────────
:ensure
%PYCMD% -c "import %~1" >nul 2>&1
if %errorlevel% == 0 (
    echo       %~2 already installed — skipping.
    exit /b 0
)
echo       Installing %~2...
%PYCMD% -m pip install %~2 --quiet
if %errorlevel% neq 0 (
    echo.
    echo  [!] Failed to install %~2
    echo      Try right-clicking setup.bat and Run as Administrator.
    echo.
    pause
    exit /b 1
)
echo       %~2 installed OK.
exit /b 0