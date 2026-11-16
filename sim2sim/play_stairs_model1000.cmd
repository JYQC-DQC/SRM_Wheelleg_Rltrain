@echo off
setlocal
cd /d "%~dp0.."
title MuJoCo - Stairs model_1000
echo Loading stairs model_1000 with its saved training configuration.
echo Use the control panel to change speed, turning and height.
"D:\Anaconda\envs\Mujoco\python.exe" -u -m tools.play_stairs --run "sim2sim\checkpoints\stairs_5f764e8_model1000" --terrain terrain --panel
if errorlevel 1 (
    echo MuJoCo could not finish normally. See the error above.
    pause
    exit /b 1
)
endlocal
