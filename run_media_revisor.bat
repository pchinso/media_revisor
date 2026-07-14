@echo off
setlocal

pushd "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=%~dp0.venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python was not found. Create the project environment first.
        popd
        pause
        exit /b 1
    )
    set "PYTHON=python"
)

"%PYTHON%" -m media_revisor
set "EXIT_CODE=%ERRORLEVEL%"

popd

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Media Revisor exited with code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%