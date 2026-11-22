@echo off
setlocal
cd /d "%~dp0.."
title P3 Jump sim2sim - Space jumps
set "pythonExe=D:\Anaconda\envs\Mujoco\python.exe"
if not exist "%pythonExe%" set "pythonExe=D:\Anaconda3\envs\mjlab\python.exe"
if not exist "%pythonExe%" set "pythonExe=python"
"%pythonExe%" -u -m tools.play_jump --run "sim2sim/checkpoints/jump_air_motion_model22400" --height 0.0925 %*
if errorlevel 1 pause
endlocal
