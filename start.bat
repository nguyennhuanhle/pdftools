@echo off
REM PDF Cleaner - Launcher
REM Starts the GUI application

cd /d "%~dp0"

REM Check for local venv first, then system Python
if exist "venv\Scripts\python.exe" (
    start "" "venv\Scripts\pythonw.exe" "%~dp0app.py"
) else if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\pythonw.exe" "%~dp0app.py"
) else (
    REM Fall back to system Python
    where pythonw >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        start "" pythonw "%~dp0app.py"
    ) else (
        echo ERROR: Python not found.
        echo Please install Python and run: pip install -r requirements.txt
        pause
        exit /b 1
    )
)
