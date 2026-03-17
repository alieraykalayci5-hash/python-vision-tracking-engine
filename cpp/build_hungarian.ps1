$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildDir = Join-Path $scriptDir "build"

if (-not (Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}

$srcFile = Join-Path $scriptDir "hungarian_bridge.cpp"
$outFile = Join-Path $buildDir "hungarian.dll"

g++ -O3 -shared -std=c++17 -static -static-libgcc -static-libstdc++ -o $outFile $srcFile

Write-Host "Built:" $outFile