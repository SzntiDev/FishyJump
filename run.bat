@echo off
title FishyJump - Instalando dependencias...
echo.
echo  =========================================
echo    FishyJump - Instalando dependencias
echo  =========================================
echo.

py -m pip install pygame-ce --quiet

if %errorlevel% neq 0 (
    echo [ERROR] No se pudo instalar pygame-ce.
    echo Asegurate de tener Python instalado y en el PATH.
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas correctamente.
echo.
title FishyJump
echo  Iniciando el juego...
echo.

py "%~dp0main.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El juego cerro con un error.
    pause
)
