@echo off
setlocal
cd /d "%~dp0"
set "model=tunnel_standard.xml"
if not "%~1"=="" set "model=tunnel_level%~1.xml"
"D:\Anaconda\envs\Mujoco\python.exe" -m mujoco.viewer --mjcf "%model%"
if errorlevel 1 pause
endlocal
