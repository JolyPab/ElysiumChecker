@echo off
set PYTHON=

py --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=py & goto :run )

python --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=python & goto :run )

for /d %%D in ("%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.*") do (
    if exist "%%D\python.exe" ( set PYTHON="%%D\python.exe" & goto :run )
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" ( set PYTHON="%%D\python.exe" & goto :run )
)

echo Python not found
pause
exit /b 1

:run
%PYTHON% main.py
