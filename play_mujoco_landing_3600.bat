@echo off
setlocal
cd /d "%~dp0runs\scut_sim2sim\landing_model3600"
if errorlevel 1 goto failed
title MuJoCo - Landing model_3600
 echo Terminal commands: set VX WZ HEIGHT / stop / reset / drop 0.10 / quit
 echo Type commands in THIS terminal. MuJoCo viewer keys are unchanged.
"D:\Anaconda\envs\Mujoco\python.exe" -m tools.scut_sim2sim --bundle . --seconds 3600
if errorlevel 1 goto failed
exit /b 0
:failed
pause
exit /b 1
