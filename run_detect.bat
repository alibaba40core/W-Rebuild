@echo off
echo Running PowerShell detection...
powershell -ExecutionPolicy Bypass -File scripts\detect.ps1 > detection_output.txt 2>&1
echo Exit code: %ERRORLEVEL%
echo.
echo Output:
type detection_output.txt
