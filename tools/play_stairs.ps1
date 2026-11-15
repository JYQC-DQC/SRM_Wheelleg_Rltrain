param(
    [string]$Python = "D:/Anaconda3/envs/mjlab/python.exe",
    [string]$Run = "",
    [string]$Profile = "flat",
    [int]$Row = 1,
    [switch]$Panel
)

$ErrorActionPreference = "Stop"
$taskRepo = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $taskRepo
try {
    if (-not $Run) {
        # Keep each checkpoint with its own saved robot/policy configuration.
        $launch = Get-Content -LiteralPath "runs/stairs_viewer/last_launch.json" -Raw | ConvertFrom-Json
        if (-not $launch.checkpoint) { throw "last_launch.json has no checkpoint; specify -Run explicitly." }
        $Run = Split-Path -Parent $launch.checkpoint
    }
    Write-Host "Checkpoint directory: $Run"
    Write-Host "Loading the highest model iteration in this directory with its saved params."
    Write-Host "Keypad 8/2: speed; 4/6: turn; 9/3: height; 5: stop. NumLock on."
    Write-Host "Letter driving keys work only in the separate control panel."
    $taskArguments = @("-m", "tools.play_stairs", "--run", $Run, "--profile", $Profile, "--row", $Row)
    if ($Panel) { $taskArguments += "--panel" }
    & $Python @taskArguments
    if ($LASTEXITCODE -ne 0) { throw "MuJoCo course viewer exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
}
