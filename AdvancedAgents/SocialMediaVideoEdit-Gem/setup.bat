@echo off
echo ==========================================
echo   Agentic Video Editor - Setup Assistant
echo ==========================================

REM Check for Docker
docker --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [X] Docker is not installed or not in PATH.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo [V] Docker is installed.

REM Check if node_modules exists locally (sign of manual npm install)
IF EXIST "frontend\node_modules" (
    echo [!] Warning: 'node_modules' folder detected in frontend. 
    echo     This might conflict with Docker if installed on Windows directly.
    echo     It is recommended to delete 'frontend\node_modules' before running with Docker.
    echo.
)

REM Check for .env file
IF EXIST .env (
    echo [V] .env file already exists.
) ELSE (
    echo [!] .env file not found.
    set /p API_KEY="Please enter your Google Gemini API Key: "
    
    IF "%API_KEY%"=="" (
        echo [X] API Key cannot be empty.
        pause
        exit /b 1
    )
    
    echo GEMINI_API_KEY=%API_KEY%> .env
    echo [V] .env file created.
)

echo ------------------------------------------
echo [!] Starting the application with Docker...
echo ------------------------------------------

docker-compose up --build
pause
