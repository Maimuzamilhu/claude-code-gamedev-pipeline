# Install every skill in this repo for Claude Code (Windows PowerShell).
#   .\install.ps1            -> your user skills folder (%USERPROFILE%\.claude\skills), every project
#   .\install.ps1 -Project   -> .\.claude\skills of the current folder (this game only)
param([switch]$Project)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($Project) { $dest = Join-Path (Get-Location) ".claude\skills" } else { $dest = Join-Path $env:USERPROFILE ".claude\skills" }
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem -Directory (Join-Path $here "skills") | ForEach-Object {
    $target = Join-Path $dest $_.Name
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse $_.FullName $target
    Write-Host "installed $($_.Name)"
}
Write-Host ""
Write-Host "Done: skills are in $dest"
Write-Host 'Open Claude Code and say: "I want to make a game. Where do I start?"'
