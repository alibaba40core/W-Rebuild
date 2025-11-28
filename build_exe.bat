@echo off
REM Build script for W-Rebuild - Windows Workspace Configuration Backup & Restore Tool
REM This script creates a standalone Windows executable using PyInstaller

echo ========================================
echo W-Rebuild - Windows Workspace Configuration Backup ^& Restore Tool
echo Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo [3/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo [4/5] Building executable...
pyinstaller W-Rebuild.spec --clean
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [5/5] Creating distribution package...
if not exist "release" mkdir "release"

REM Copy executable and required files
xcopy /E /I /Y "dist\W-Rebuild\*" "release\"

REM Create README for release
echo W-Rebuild - Windows Workspace Configuration Backup ^& Restore Tool v1.0 > "release\README.txt"
echo. >> "release\README.txt"
echo Installation: >> "release\README.txt"
echo 1. Extract all files to a folder on your Windows machine >> "release\README.txt"
echo 2. Run W-Rebuild.exe >> "release\README.txt"
echo. >> "release\README.txt"
echo Features: >> "release\README.txt"
echo - Detect installed tools and workspace configurations >> "release\README.txt"
echo - Backup complete workspace to OneDrive/local folder >> "release\README.txt"
echo - Restore entire workspace on new Windows machines >> "release\README.txt"
echo. >> "release\README.txt"
echo For more information, visit: https://github.com/alibaba40core/W-Rebuild >> "release\README.txt"

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\W-Rebuild\W-Rebuild.exe
echo Release package: release\
echo.
echo You can now:
echo 1. Test the executable: dist\W-Rebuild\W-Rebuild.exe
echo 2. Create ZIP: Compress the 'release' folder
echo 3. Upload to GitHub releases
echo.
pause
