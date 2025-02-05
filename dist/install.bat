@echo off
setlocal enabledelayedexpansion

:: Ellenőrizzük, hogy admin módban fut-e a script
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo =====================================================
    echo ERROR: This script must be run as Administrator!
    echo =====================================================
    pause
    exit /b
)

:: Ellenőrizzük, hogy Chocolatey telepítve van-e
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo =====================================================
    echo Chocolatey is not installed. Installing Chocolatey...
    echo =====================================================
    
    powershell -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

    :: Várunk, hogy befejeződjön a telepítés
    timeout /t 10

    :: Frissítjük a környezeti változókat, hogy elérhessük a choco-t
    call C:\ProgramData\chocolatey\bin\refreshenv.cmd

    :: Újra ellenőrizzük, hogy a Chocolatey telepítve van-e
    where choco >nul 2>&1
    if %errorlevel% neq 0 (
        echo =====================================================
        echo ERROR: Chocolatey installation failed.
        echo =====================================================
        pause
        exit /b
    )
)

:: Telepítjük az Ngrok-ot, ha még nincs telepítve
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ===================================
    echo Ngrok is not installed. Installing...
    echo ===================================
    
    powershell -Command "choco install ngrok -y"
    
    :: Várunk, hogy befejeződjön az Ngrok telepítése
    timeout /t 10

    :: Ellenőrizzük, hogy az Ngrok telepítve van-e
    where ngrok >nul 2>&1
    if %errorlevel% neq 0 (
        echo =====================================================
        echo ERROR: Ngrok installation failed.
        echo =====================================================
        pause
        exit /b
    )
)

:: Frissítjük a környezeti változókat
call C:\ProgramData\chocolatey\bin\refreshenv.cmd

echo =========================================================
echo All required tools (Chocolatey, Ngrok) have been installed.
echo Now launching the application in a new CMD window...
echo =========================================================

:: Új CMD ablakot indítunk, hogy friss környezeti változókkal futtassuk a programot
start cmd /k "start /b ngrok http 5000 & start /b solana_wallet_tracker.exe"

exit