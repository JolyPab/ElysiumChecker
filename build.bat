@echo off
echo ================================================
echo   ElysiumChecker - Build Script
echo ================================================
echo.

:: --- Find Python ---
set PYTHON=

:: Try py launcher first
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    goto :found_python
)

:: Try python
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python
    goto :found_python
)

:: Try python3
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python3
    goto :found_python
)

:: Try Windows Store / AppData path
for /d %%D in ("%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.*") do (
    if exist "%%D\python.exe" (
        set PYTHON="%%D\python.exe"
        goto :found_python
    )
)

:: Try common local installs
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set PYTHON="%%D\python.exe"
        goto :found_python
    )
)

echo [ERROR] Python not found in PATH or common locations.
echo Ensure Python is installed and added to PATH.
pause
exit /b 1

:found_python
echo [OK] Python found: %PYTHON%
%PYTHON% --version

:: Create tools folder if missing
if not exist "tools" (
    mkdir tools
    echo [INFO] Created tools\ folder - place utility .exe files there
)

:: Install deps
echo.
echo [1/3] Installing dependencies...
%PYTHON% -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

:: Check tools folder
if not exist "tools" mkdir tools
set TOOL_COUNT=0
for %%F in (tools\*.exe) do set /a TOOL_COUNT+=1
if %TOOL_COUNT%==0 (
    echo [WARN] Папка tools\ пустая - утилиты не будут включены в .exe
    echo        Положи .exe утилиты в tools\ перед билдом
    echo.
)

:: Collect logo flags
set LOGO_FLAGS=
if exist "logo.gif" set LOGO_FLAGS=%LOGO_FLAGS% --add-data "logo.gif;."
if exist "logo.png" set LOGO_FLAGS=%LOGO_FLAGS% --add-data "logo.png;."

:: Build
echo [2/3] Building executable...
%PYTHON% -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "ElysiumChecker" ^
    --icon "logo.ico" ^
    --add-data "logo.ico;." ^
    --add-data "config.json;." ^
    --add-data "pages;pages" ^
    --add-data "utils;utils" ^
    --add-data "tools;tools" ^
    %LOGO_FLAGS% ^
    --hidden-import "win32gui" ^
    --hidden-import "win32con" ^
    --hidden-import "win32api" ^
    --hidden-import "win32process" ^
    --hidden-import "psutil" ^
    --collect-all "PyQt5" ^
    main.py

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo [3/3] Done!
echo.
echo Output: dist\ElysiumChecker.exe
echo.
echo IMPORTANT: Copy the "tools" folder next to ElysiumChecker.exe
echo ================================================
pause
