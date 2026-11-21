@echo off
setlocal
cd /d "%~dp0.."
title MuJoCo - Multi Actor Jump 6200 + Landing 5800
"D:\Anaconda\envs\Mujoco\python.exe" -u -m tools.play_jump --run "sim2sim/checkpoints/jump_multi_actor_model6200" --height 0.04 --handoff-vertical-speed 0.3 %*
if errorlevel 1 pause
endlocal
