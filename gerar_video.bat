@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Execute gerar_teste.bat primeiro.
 pause
 exit /b 1
)
if not exist config.json copy config.example.json config.json >nul
.venv\Scripts\python.exe -m darkstudio.cli --config config.json
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo Consulte a mensagem de erro e os arquivos preservados em outputs.
pause
exit /b %RESULT%
