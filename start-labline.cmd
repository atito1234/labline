@echo off
REM ============================================================
REM  LabLine one-click launcher (Windows)
REM  Starts the web server + the Ollama search proxy, then opens
REM  the app. Double-click this file to run everything.
REM
REM  ONE-TIME SETUP so web search works without retyping a key:
REM     setx OLLAMA_API_KEY "your-ollama-key"
REM  ...then close and reopen this launcher (setx needs a fresh window).
REM  Leave OLLAMA_API_KEY unset to run without web search.
REM ============================================================
cd /d "%~dp0"

if "%OLLAMA_API_KEY%"=="" (
  echo [!] OLLAMA_API_KEY is not set - web research will be OFF.
  echo     To enable it: setx OLLAMA_API_KEY "your-key"  then reopen this launcher.
  echo.
)

start "LabLine search proxy" cmd /k python tools\ollama-search-proxy.py
start "LabLine web server"  cmd /k python -m http.server 8000
timeout /t 2 >nul
start "" http://localhost:8000/app/

echo LabLine is starting in two windows (proxy + web server).
echo Close those windows to stop it. This launcher window can be closed.
timeout /t 3 >nul
