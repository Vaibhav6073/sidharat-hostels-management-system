@echo off
title Sidharat Hostels - Installation
color 0A

echo.
echo ========================================
echo   SIDHARAT HOSTELS MANAGEMENT SYSTEM
echo           INSTALLATION
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

echo Python found! Installing dependencies...
echo.

pip install Flask >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install Flask
    echo Please check your internet connection
    pause
    exit /b 1
)

echo Creating database...
python -c "from app import init_db; init_db(); print('Database created successfully!')"

echo.
echo ========================================
echo        INSTALLATION COMPLETE!
echo ========================================
echo.
echo To start the application:
echo 1. Double-click START.bat
echo 2. Or run: python app.py
echo.
echo Access URLs:
echo - Computer: http://localhost:5000
echo - Mobile: Use mobile_run.bat for IP
echo.
pause