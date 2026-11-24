@echo off
setlocal
cd /d "%~dp0.."
set "terrainRow=2"
if not "%~1"=="" set "terrainRow=%~1"
title MuJoCo - Edge speed model_1400
echo Loading edge speed model_1400 with terrain and saved training configuration.
"D:\Anaconda\envs\Mujoco\python.exe" -u -m tools.play_stairs --run "sim2sim\checkpoints\stairs_edge_speed_model1400" --terrain terrain --terrain-group stairs --row "%terrainRow%" --panel
if errorlevel 1 (
    echo MuJoCo could not finish normally. See the error above.
    pause
    exit /b 1
)
endlocal
