@echo off
REM CogniFlow Quick Start Script for Windows
REM This script helps you set up and run CogniFlow with Docker

echo.
echo ========================================
echo    CogniFlow Quick Start
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker is not installed. Please install Docker Desktop first:
    echo     https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [*] Docker is installed
echo.

REM Check if .env exists
if not exist .env (
    echo [*] Creating .env file from template...
    copy .env.example .env
    echo.
    echo [!] IMPORTANT: Please edit .env file and add your GEMINI_API_KEY
    echo.
    pause
)

echo [*] Building Docker containers...
docker-compose build

echo.
echo [*] Starting CogniFlow...
docker-compose up -d

echo.
echo [*] Waiting for services to be ready...
timeout /t 5 /nobreak >nul

echo.
echo [+] CogniFlow is running!
echo.
echo Access the application:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Useful commands:
echo   View logs:        docker-compose logs -f
echo   Stop services:    docker-compose down
echo   Restart:          docker-compose restart
echo.
pause
