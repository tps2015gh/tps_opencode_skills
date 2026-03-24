@echo off
REM Install skills to another project
REM Usage: install.bat C:\other_project

if "%~1"=="" (
    echo Usage: install.bat C:\path\to\project
    exit /b 1
)

set TARGET=%~1

echo Copying .opencode to %TARGET%\.opencode ...
xcopy /E /I /Y ".opencode" "%TARGET%\.opencode"

if exist ".env" (
    echo Copying .env ...
    copy /Y ".env" "%TARGET%\.env"
)

echo Done. Restart OpenCode in %TARGET%
