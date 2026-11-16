@echo off
setlocal
cd /d "%~dp0runs\scut_sim2sim\landing_tune_model5800"
if errorlevel 1 goto failed
title MuJoCo - Landing tune model_5800
 echo Current run: landing tune 20261113_143050 - model_5800
 echo Terminal commands: set VX WZ HEIGHT / stop / reset / drop 0.10 / quit
 echo Type commands in THIS terminal. MuJoCo viewer keys are unchanged.
"D:\Anaconda\envs\Mujoco\python.exe" -m tools.scut_sim2sim --bundle "%cd%" --seconds 3600
if errorlevel 1 goto failed
exit /b 0
:failed
pause
exit /b 1
