@echo off
REM Install all skills to another project
REM Usage: install.bat C:\path\to\project

if "%~1"=="" (
    echo.
    echo TPS OpenCode Skills Installer
    echo ==============================
    echo.
    echo Usage: install.bat C:\path\to\project
    echo.
    echo Examples:
    echo   install.bat C:\my_webapp
    echo   install.bat C:\Projects\shop_system
    echo   install.bat D:\work\client_project
    echo.
    echo This copies all skills to your project:
    echo   - telegram-send   (send messages to Telegram)
    echo   - queue-check     (check inbox queue)
    echo   - queue-notify    (background queue monitor)
    echo   - file-list       (list files)
    echo   - thai-tts        (text-to-speech)
    echo   - play-audio      (play audio files)
    echo   - piano           (play piano notes)
    echo   - html-report     (create HTML reports)
    echo   - html-to-facebook (convert reports to Facebook posts)
    echo   - pdf-to-telegram (list PDFs and send to Telegram)
    echo   - mysql-query     (execute MySQL queries)
    echo.
    echo For mysql-query, setup mysql.exe path after install:
    echo   python .opencode\skills\mysql-query\mysql_query.py setup "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    echo.
    exit /b 1
)

set TARGET=%~1

echo.
echo Copying .opencode to %TARGET%\.opencode ...
xcopy /E /I /Y ".opencode" "%TARGET%\.opencode"

if exist ".env" (
    echo Copying .env ...
    copy /Y ".env" "%TARGET%\.env"
)

echo.
echo Done! All skills installed to %TARGET%
echo.
echo Next steps:
echo   1. Restart OpenCode in %TARGET%
echo   2. For mysql-query, setup path:
echo      python .opencode\skills\mysql-query\mysql_query.py setup "C:\path\to\mysql.exe"
echo.
