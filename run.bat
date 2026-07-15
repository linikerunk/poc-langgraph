@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === LangChain SRE POC ===
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python is not on PATH. Install Python 3.12+ and try again.
  goto :fail
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtualenv...
  python -m venv .venv
  if errorlevel 1 (
    echo ERROR: Failed to create .venv
    goto :fail
  )
  call .venv\Scripts\activate.bat
  echo Installing dependencies...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo ERROR: pip install failed
    goto :fail
  )
) else (
  call .venv\Scripts\activate.bat
)

if not exist ".env" (
  copy .env.example .env >nul
  echo Created .env from .env.example - add OPENAI_API_KEY for LLM features.
  echo.
)

REM Free port 8000 if a previous server is still running
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
  echo Port 8000 is in use by PID %%P - stopping it...
  taskkill /PID %%P /F >nul 2>&1
)

echo.
echo Starting API at http://localhost:8000/docs
echo Press Ctrl+C to stop.
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
if errorlevel 1 goto :fail
goto :eof

:fail
echo.
echo Startup failed. See messages above.
pause
exit /b 1
