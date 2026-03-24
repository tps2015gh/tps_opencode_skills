@echo off
REM Install mysql-query skill to project
REM Usage: install.bat C:\path\to\project

if "%~1"=="" (
    echo.
    echo MySQL Query Skill Installer
    echo ============================
    echo.
    echo Usage: install.bat C:\path\to\project
    echo.
    echo Examples:
    echo   install.bat C:\my_webapp
    echo   install.bat C:\Projects\shop_system
    echo.
    echo After install, setup mysql.exe path:
    echo   python .opencode\skills\mysql-query\mysql_query.py setup "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    echo.
    echo Common mysql.exe paths:
    echo   C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
    echo   C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe
    echo   C:\xampp\mysql\bin\mysql.exe
    echo   C:\wamp64\bin\mysql\mysql8.0.31\bin\mysql.exe
    echo.
    exit /b 1
)

set TARGET=%~1
set SKILL_DIR=%~dp0

echo.
echo Installing mysql-query to %TARGET% ...
echo.

if not exist "%TARGET%\.opencode\skills\mysql-query" (
    mkdir "%TARGET%\.opencode\skills\mysql-query"
)

copy /Y "%SKILL_DIR%mysql_query.py" "%TARGET%\.opencode\skills\mysql-query\"
copy /Y "%SKILL_DIR%SKILL.md" "%TARGET%\.opencode\skills\mysql-query\"

echo.
echo Done! mysql-query skill installed.
echo.
echo Next steps:
echo   1. Setup mysql.exe path:
echo      python .opencode\skills\mysql-query\mysql_query.py setup "C:\path\to\mysql.exe"
echo.
echo   2. Connect and query:
echo      python .opencode\skills\mysql-query\mysql_query.py connect
echo      python .opencode\skills\mysql-query\mysql_query.py query "SHOW TABLES"
echo.
