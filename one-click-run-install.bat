@echo off
SET venv_dir=venv
SET pyfile=upload.py
SET python=%venv_dir%\Scripts\python.exe

@echo off


REM 5 second timer with a message
ECHO Press Enter key within 5 seconds to open the menu...
ECHO .
ECHO Otherwise the menu will setup/launch app automatically.
ECHO .
SET /P "=Press Enter to continue..." <nul
PING 127.0.0.1 -n 6 >nul

REM Check if the virtual environment directory exists
IF EXIST "%venv_dir%\Scripts\activate.bat" (
    ECHO Virtual environment found. Activating...
    CALL %venv_dir%\Scripts\activate.bat
) ELSE (
    ECHO Creating virtual environment...
    python -m venv %venv_dir%
    CALL %venv_dir%\Scripts\activate.bat
)
REM Check if Enter was pressed by detecting the error level
IF ERRORLEVEL 1 (
    GOTO MainRoutine
) ELSE (
    GOTO Menu
)

:Menu
CLS
@echo off


ECHO [1] Open Enviroment To Install Packages
ECHO [2] Auto Install Torch
ECHO [3] Exit
ECHO Please select an option:
SET /P menuChoice="Type option number and press Enter: "
IF "%menuChoice%"=="1" (
    CLS
    REM Further commands as required to open the environment or otherwise stated action
) ELSE IF "%menuChoice%"=="2" (
    %python% -m pip install --upgrade --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Failed to install Torch. Check your internet connection or Python installation.
        PAUSE
    )
) ELSE IF "%menuChoice%"=="3" (
    EXIT
) ELSE (
    ECHO Invalid option. Please try again.
    GOTO MainRoutine
)
GOTO End

:MainRoutine
CLS
@echo off

REM Check if the virtual environment is activated
IF NOT "%VIRTUAL_ENV%" == "" (
    ECHO Virtual environment activated.
    ECHO Installing dependencies...
    %python% -m pip install --upgrade pip
    %python% -m pip install -r requirements.txt
    ECHO Dependencies installed.
    
    REM Check if the specified pyfile exists, if not, find the first .py file except __init__.py
    IF NOT EXIST "%pyfile%" (
        FOR /F "delims=" %%i IN ('DIR *.py /B /A:-D /O:N 2^>nul') DO (
            IF NOT "%%i" == "__init__.py" (
                SET "pyfile=%%i"
                GOTO FoundPyFile
            )
        )
        ECHO No suitable Python file found. Exiting...
        GOTO End
    )
    
    :FoundPyFile
    REM Run the Python script
    %python% -m pip install --upgrade pip
    %python% %pyfile%
) ELSE (
    ECHO Failed to activate virtual environment.
)

:End
REM Pause the command window
cmd /k 
