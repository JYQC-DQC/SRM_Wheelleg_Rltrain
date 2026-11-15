@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools/play_stairs.ps1" -Profile up_one -Row 2 -Panel %*
if errorlevel 1 (
    echo.
    echo Sim2sim failed. See the error above.
    pause
    exit /b 1
)
endlocal
