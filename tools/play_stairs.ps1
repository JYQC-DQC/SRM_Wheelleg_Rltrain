param(
    [string]$Python = "python",
    [string]$Run = "runs/stairs_viewer/checkpoint",
    [string]$Profile = "up_one",
    [int]$Row = 2,
    [switch]$Panel
)

$ErrorActionPreference = "Stop"
$taskRepo = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $taskRepo
try {
    $taskArguments = @("-m", "tools.play_stairs", "--run", $Run, "--profile", $Profile, "--row", $Row)
    if ($Panel) { $taskArguments += "--panel" }
    & $Python @taskArguments
    if ($LASTEXITCODE -ne 0) { throw "MuJoCo course viewer exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
}
