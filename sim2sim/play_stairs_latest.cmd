@echo off
setlocal
cd /d "%~dp0.."
title MuJoCo - Stairs model_2000
echo Loading stairs model_2000 with terrain and saved training configuration.
"D:\Anaconda\envs\Mujoco\python.exe" -u -m tools.play_stairs --run "sim2sim\checkpoints\stairs_5f764e8_model2000" --terrain terrain --terrain-group stairs --panel
if errorlevel 1 (
    echo MuJoCo could not finish normally. See the error above.
    pause
    exit /b 1
)
endlocal
