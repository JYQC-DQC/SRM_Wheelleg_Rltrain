@echo off
setlocal
cd /d "%~dp0.."
title P3 Jump sim2sim - Space jumps
set "pythonExe=D:\Anaconda\envs\Mujoco\python.exe"
if not exist "%pythonExe%" set "pythonExe=python"
"%pythonExe%" -u -m tools.play_jump %*
if errorlevel 1 pause
endlocal
