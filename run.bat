@echo off
setlocal
set SCRIPT_DIR=%~dp0
rem Keep PowerShell open after script completes so errors are visible
powershell -NoProfile -ExecutionPolicy Bypass -NoExit -File "%SCRIPT_DIR%scripts\run.ps1"
endlocal
