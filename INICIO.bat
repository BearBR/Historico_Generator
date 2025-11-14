@echo off
chcp 65001 > nul
cls
echo ========================================
echo  Historico Generator - Servidor Flask
echo ========================================
echo.

REM Ativar ambiente virtual
echo [*] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Abrir navegador após 3 segundos em background
echo [*] Iniciando servidor Flask...
start /B cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000"
echo.
echo ========================================
echo  Servidor rodando em http://127.0.0.1:5000
echo  Pressione CTRL+C para parar
echo ========================================
echo.

:loop
REM Iniciar o servidor e capturar código de saída
python app.py

REM Verificar se o servidor foi fechado intencionalmente (CTRL+C) ou por erro
if errorlevel 1 (
    echo.
    echo [!] Erro detectado! Reiniciando servidor em 5 segundos...
    echo [!] Pressione CTRL+C para cancelar
    timeout /t 5
    goto loop
) else (
    echo.
    echo [*] Servidor encerrado normalmente.
    pause
    exit /b 0
)
