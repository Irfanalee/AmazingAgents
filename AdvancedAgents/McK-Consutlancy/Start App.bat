@echo off
REM Windows double-click launcher for NPI Strategy Suite

REM Move to the directory containing this script
cd /d "%~dp0"

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found.
    echo Please run the first-time setup from HOW_TO_RUN.md first.
    echo.
    pause
    exit /b 1
)

echo Starting NPI Strategy Suite on http://localhost:8000 ...
echo Press Ctrl+C to stop.
echo.

REM Open browser after a short delay
start "" /b cmd /c "timeout /t 2 >nul && start http://localhost:8000"

uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
