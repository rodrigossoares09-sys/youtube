@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
py -3 --version >nul 2>&1
if errorlevel 1 (
 echo Instale Python 3.11 ou superior em python.org, incluindo o Python Launcher.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
 py -3 -m venv .venv
 if errorlevel 1 goto :error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
if not exist config.json copy config.example.json config.json >nul
.venv\Scripts\python.exe -m darkstudio.cli --config config.json --test
if errorlevel 1 goto :error
echo.
echo Teste concluido. Abra a pasta outputs e revise o resultado.
pause
exit /b 0
:error
echo.
echo Nao foi possivel concluir. Leia a mensagem acima e consulte docs\WINDOWS.md.
pause
exit /b 1
