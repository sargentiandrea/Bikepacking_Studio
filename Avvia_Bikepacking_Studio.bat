@echo off
title Bikepacking Studio - Native Desktop
echo Starting Bikepacking Studio...
cd "C:\Users\sarge\Desktop\Bikepacking_Studio"
python app_desktop.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRORE] Impossibile avviare l'applicazione.
    echo Assicurati che Python sia installato e aggiunto alle variabili d'ambiente.
    pause
)