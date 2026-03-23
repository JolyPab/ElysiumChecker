@echo off
echo Installing dependencies for ElysiumChecker...
echo.

set PYTHON=

py --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=py & goto :install )

python --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=python & goto :install )

for /d %%D in ("%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.*") do (
    if exist "%%D\python.exe" ( set PYTHON="%%D\python.exe" & goto :install )
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" ( set PYTHON="%%D\python.exe" & goto :install )
)

echo [ERROR] Python not found
pause
exit /b 1

:install
echo Using: %PYTHON%
%PYTHON% -m pip install PyQt5 requests psutil pywin32 pyinstaller
echo.
echo Done! Now run build.bat
pause
