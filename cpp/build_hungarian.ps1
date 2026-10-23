$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildDir = Join-Path $scriptDir "build"
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
$src = Join-Path $scriptDir "hungarian_bridge.cpp"
$out = Join-Path $buildDir "hungarian.dll"
if (-not (Get-Command g++ -ErrorAction SilentlyContinue)) {
    throw "g++ not found. Install MinGW-w64 or use the SciPy fallback (no native compilation required)."
}
& g++ -O3 -shared -std=c++17 -o $out $src
if ($LASTEXITCODE -ne 0) { throw "C++ compilation failed" }
Write-Host "Built: $out"
