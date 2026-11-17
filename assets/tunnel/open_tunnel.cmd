@echo off
setlocal
cd /d "%~dp0"
set "model=tunnel_standard.xml"
"D:\Anaconda\envs\Mujoco\python.exe" -m mujoco.viewer --mjcf "%model%"
if errorlevel 1 pause
endlocal
