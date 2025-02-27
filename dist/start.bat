@echo off

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

:: Set the ngrok authtoken
echo Setting ngrok authtoken...
ngrok authtoken %token%

:: Start ngrok in the foreground to see the link
echo Starting ngrok...
start cmd /k ngrok http 5000

:: Give ngrok a few seconds to initialize before running the executable
timeout /t 5

:: Start the exe file
echo Starting the exe...
start "" /b solana_wallet_tracker.exe

:: Keep ngrok running in the background even after the exe has started
echo Ngrok is still running in the background.
pause
exit