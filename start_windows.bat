@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Python Vision Tracking Engine

echo =======================================================
echo  Python Vision Tracking Engine - Windows Quick Start
echo =======================================================
echo.
set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    py -3.12 --version >nul 2>nul && set "PYTHON_CMD=py -3.12"
    if not defined PYTHON_CMD py -3.11 --version >nul 2>nul && set "PYTHON_CMD=py -3.11"
    if not defined PYTHON_CMD py -3.10 --version >nul 2>nul && set "PYTHON_CMD=py -3.10"
)
if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    echo [ERROR] Python 3.10-3.12 is required. Install from https://www.python.org/downloads/
    goto :failed
)
if not exist ".venv\Scripts\python.exe" (
    echo [SETUP] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :failed
)
if not exist ".venv\.requirements_ready" (
    echo [SETUP] Installing PyTorch, OpenCV, Ultralytics and other dependencies...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :failed
    echo setup-complete> ".venv\.requirements_ready"
)
if not exist "data\input\sample_video.mp4" (
    echo [INFO] No sample video found. Generating synthetic example.
    ".venv\Scripts\python.exe" tools\make_synthetic_demo.py
    if errorlevel 1 goto :failed
)
echo [START] Press Q in the preview window to stop.
".venv\Scripts\python.exe" main.py
if errorlevel 1 goto :failed
echo.
echo [DONE] Output: data\output\tracked_video.mp4
echo [NOTE] Synthetic samples may not trigger person detections.
pause
exit /b 0
:failed
echo.
echo [ERROR] Could not start. Read the message above.
pause
exit /b 1
