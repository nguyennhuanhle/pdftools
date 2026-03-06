@echo off
REM PDF Tools - Build Windows Executable
REM Creates PDFTools.exe in the dist\ folder

cd /d "%~dp0"

echo ============================================
echo   PDF Tools - Building Windows Executable
echo ============================================
echo.

REM Determine Python path
if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
    set PIP=venv\Scripts\pip.exe
) else if exist ".venv\Scripts\python.exe" (
    set PYTHON=.venv\Scripts\python.exe
    set PIP=.venv\Scripts\pip.exe
) else (
    set PYTHON=python
    set PIP=pip
)

REM Install PyInstaller if not present
echo [1/3] Checking PyInstaller...
%PIP% show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo       Installing PyInstaller...
    %PIP% install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
)
echo       PyInstaller OK.
echo.

REM Clean previous build
echo [2/3] Cleaning previous build...
if exist "dist\PDFTools.exe" del /q "dist\PDFTools.exe"
if exist "build" rmdir /s /q "build"
echo       Done.
echo.

REM Build executable
echo [3/3] Building PDFTools.exe (this may take a few minutes)...
echo.
%PYTHON% -m PyInstaller build.spec --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed! Check the output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build completed successfully!
echo   Output: dist\PDFTools.exe
echo ============================================
echo.
pause
