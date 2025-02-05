@echo off

:: Check if ngrok is installed via Chocolatey
choco list --local-only ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo Ngrok is not installed. Installing ngrok via Chocolatey...
    powershell -Command "Start-Process choco -ArgumentList 'install ngrok -y' -Wait -WindowStyle Hidden"
)

:: Check if ngrok_token.txt exists and is not empty
if not exist "ngrok_token.txt" (
    echo Ngrok token file not found! Please create ngrok_token.txt and add your token inside it.
    exit /b
)

:: Read the token from ngrok_token.txt
for /f "delims=" %%i in (ngrok_token.txt) do set token=%%i

:: Check if the token is empty
if "%token%"=="" (
    echo The ngrok token is empty in the ngrok_token.txt file. Please provide a valid token.
    exit /b
)

:: Set the ngrok authtoken silently
ngrok authtoken %token% >nul 2>&1

:: Start ngrok in the background (using start command)
start /b ngrok http 5000

:: Give ngrok a few seconds to initialize before running the executable
timeout /t 5 >nul 2>&1

:: Start the exe file with noconsole
start /B solana_wallet_tracker.exe

:: Keep ngrok running in the background even after the exe has started
echo Ngrok is still running in the background.
pause
exit