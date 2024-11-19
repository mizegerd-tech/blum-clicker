@echo off
SETLOCAL

REM Define Python installer file name (change this according to your actual Python installer file name)
SET PYTHON_INSTALLER=python-3.12.4.exe

REM Check if Python is already installed
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    REM Install Python
    echo Installing Python...
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1

    REM Verify Python installation
    where python >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install Python. Exiting...
        pause
        exit /b 1
    )
) ELSE (
    echo Python is already installed.
)

REM Ensure pip is upgraded
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install packages from requirements.txt
echo Installing packages from requirements.txt...
python -m pip install -r requirements.txt

REM Run the main Python script
echo Running main.py...
python main.py

REM End the script
pause
ENDLOCAL
exit /b
