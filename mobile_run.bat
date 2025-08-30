@echo off
echo Starting Sidharat Hostels for Mobile Access...
echo.

echo Finding your IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%

echo.
echo ========================================
echo   MOBILE ACCESS INSTRUCTIONS
echo ========================================
echo.
echo 1. Connect mobile to same WiFi
echo 2. Open mobile browser
echo 3. Go to: http://%IP%:5000
echo.
echo ========================================
echo.
echo Starting server...
python app.py