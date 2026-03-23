@echo off
chcp 65001 >nul
echo ========================================
echo   Thai TTS Reader
echo ========================================
echo.

if "%~1"=="" (
    echo Usage: tts.bat filename.txt [voice] [rate] [volume]
    echo.
    echo Example: tts.bat news.txt
    echo          tts.bat news.txt female +10%% +0%%
    echo.
    echo Voice: female (default) or male
    echo Rate:  +0%% (default), +10%%, -10%%
    echo Volume: +0%% (default), +20%%, -20%%
    pause
    exit /b 1
)

set PYTHONIOENCODING=utf-8
python "%~dp0thai_tts.py" %*
