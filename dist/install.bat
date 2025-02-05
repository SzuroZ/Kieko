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
    
    :: PowerShell segítségével telepítjük a Chocolatey-t, és közvetlenül a kimenetét is látjuk
    powershell -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

    :: Ellenőrizzük, hogy sikerült-e a telepítés
    where choco >nul 2>&1
    if %errorlevel% neq 0 (
        echo =====================================================
        echo ERROR: Chocolatey installation failed.
        echo Please check manually.
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
    
    :: PowerShell segítségével telepítjük az Ngrok-ot, és közvetlenül látjuk a kimenetet
    powershell -Command "choco install ngrok -y"
    
    :: Ellenőrizzük, hogy sikerült-e telepíteni az Ngrok-ot
    where ngrok >nul 2>&1
    if %errorlevel% neq 0 (
        echo =====================================================
        echo ERROR: Ngrok installation failed.
        echo Please check your Chocolatey installation.
        echo =====================================================
        pause
        exit /b
    )
)

:: Frissítjük a környezeti változókat
call C:\ProgramData\chocolatey\bin\refreshenv.cmd

echo =========================================================
echo All required tools (Chocolatey, Ngrok) have been installed.
echo You can now run the application script.
echo =========================================================
pause
exit
