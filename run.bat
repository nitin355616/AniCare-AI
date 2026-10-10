@echo off
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
set BACKEND_DIR=%ROOT_DIR%backend
set VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment Python not found at %VENV_PYTHON%
    exit /b 1
)

if "%1"=="" goto start_all
if "%1"=="backend" goto start_backend
if "%1"=="frontend" goto start_frontend
if "%1"=="test" goto run_tests
if "%1"=="eval-model" goto eval_model
if "%1"=="train-model" goto train_model
if "%1"=="manifests" goto run_manifests

echo ========================================================
echo AniCare AI - CLI Launcher
echo ========================================================
echo Usage:
echo   run.bat              - Start both backend and frontend
echo   run.bat backend      - Start FastAPI backend (port 8000)
echo   run.bat frontend     - Start Vite frontend (port 5173)
echo   run.bat test         - Run full pytest automated test suite
echo   run.bat manifests    - Inspect and regenerate dataset manifests
echo   run.bat eval-model   - Evaluate disease classifier on test split
echo   run.bat train-model  - Train disease classifier on verified dataset
exit /b 0

:start_all
echo [1/2] Starting AniCare AI Backend on http://127.0.0.1:8000 ...
start "AniCare AI Backend" cmd /k "cd /d "%BACKEND_DIR%" && "%VENV_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
echo [2/2] Starting AniCare AI Frontend on http://localhost:5173 ...
start "AniCare AI Frontend" cmd /k "cd /d "%ROOT_DIR%" && npm run dev"
echo Both services launched in separate windows!
exit /b 0

:start_backend
echo Starting AniCare AI Backend on http://127.0.0.1:8000 ...
cd /d "%BACKEND_DIR%"
"%VENV_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
exit /b 0

:start_frontend
echo Starting AniCare AI Frontend on http://localhost:5173 ...
cd /d "%ROOT_DIR%"
npm run dev
exit /b 0

:run_tests
echo Running full test suite...
cd /d "%ROOT_DIR%"
"%VENV_PYTHON%" -m pytest backend/tests -v
exit /b 0

:run_manifests
echo Generating reproducible dataset manifests...
cd /d "%BACKEND_DIR%"
"%VENV_PYTHON%" scripts\generate_dataset_manifests.py
exit /b 0

:eval_model
echo Evaluating Task A disease classifier on held-out test split...
cd /d "%BACKEND_DIR%"
"%VENV_PYTHON%" scripts\train_disease_classifier.py --eval-only
exit /b 0

:train_model
echo Training Task A disease classifier...
cd /d "%BACKEND_DIR%"
"%VENV_PYTHON%" scripts\train_disease_classifier.py --epochs 4 --batch-size 32
exit /b 0
