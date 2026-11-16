@echo off
setlocal
cd /d "%~dp0.."
set "terrainRow=2"
if not "%~1"=="" set "terrainRow=%~1"
title MuJoCo - stairs model_2000
"D:\Anaconda\envs\Mujoco\python.exe" -u -m tools.play_stairs --run "sim2sim\checkpoints\stairs_5f764e8_model2000" --terrain terrain --terrain-group stairs --row "%terrainRow%" --panel
if errorlevel 1 (
    pause
    exit /b 1
)
endlocal
