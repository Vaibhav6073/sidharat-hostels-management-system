@echo off
title Sidharat Hostels Management System
color 0B

echo.
echo ========================================
echo   SIDHARAT HOSTELS MANAGEMENT SYSTEM
echo ========================================
echo.
echo Starting server...
echo.
echo Access URLs:
echo - Computer: http://localhost:5000
echo - Mobile: Use mobile_run.bat for IP address
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

echo.
echo Server stopped. Press any key to exit...
pause >nul