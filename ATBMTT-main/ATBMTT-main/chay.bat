@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py run_gui.py
) else (
    python run_gui.py
)
if errorlevel 1 pause
