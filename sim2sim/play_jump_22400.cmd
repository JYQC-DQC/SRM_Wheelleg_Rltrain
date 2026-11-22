@echo off
setlocal
cd /d "%~dp0.."
title P3 Jump 22400 - Space jumps
"D:\Anaconda\envs\Mujoco\python.exe" -u -m tools.play_jump --run "sim2sim/checkpoints/jump_air_motion_model22400" --height 0.0925 %*
if errorlevel 1 pause
endlocal
