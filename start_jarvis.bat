@echo off
title JARVIS 2.0 Launcher
echo ===================================================
echo             JARVIS 2.0 INITIALIZATION
echo ===================================================
echo.

cd /d "%~dp0"

:: Check for Python installation
python --version >nul 2>&1
if errorlevel 1 goto nopython

:: Create virtual environment if it doesn't exist
if exist venv goto activate
echo [INFO] Creating Python virtual environment (venv)...
python -m venv venv
if errorlevel 1 goto venvfail
echo [INFO] Virtual environment created successfully.

:: Initial package installation for new venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate
echo [INFO] Installing required packages...
pip install -r requirements.txt
if errorlevel 1 goto pipfail
goto runserver

:activate
echo [INFO] Activating virtual environment...
call venv\Scripts\activate
goto runserver

:runserver
echo.
echo [SUCCESS] All systems check passed. Starting Jarvis server...
echo.
python app.py
goto end

:nopython
echo [ERROR] Python is not installed or not in system PATH.
echo Please install Python and try again.
goto pauseend

:venvfail
echo [ERROR] Failed to create virtual environment.
goto pauseend

:pipfail
echo [ERROR] Dependency installation failed.
goto pauseend

:pauseend
pause

:end
