@echo off
chcp 65001 > nul

rem ---- パスをあなたの環境に固定 ----
set "PYEXE=C:\Users\shino\AppData\Local\Programs\Python\Python311\python.exe"
set "WORK=C:\Users\shino\python-tools"

rem ---- タイムスタンプ付きログを作成 ----
for /f %%a in ('powershell -NoP -C "(Get-Date).ToString(\"yyyyMMdd_HHmmss\")"') do set TS=%%a
set "LOG=%WORK%\logs\scrape_%TS%.txt"

mkdir "%WORK%\logs" 2>nul
cd /d "%WORK%"

echo [%date% %time%] scrape start >> "%LOG%"
"%PYEXE%" "%WORK%\news_scraper.py" >> "%LOG%" 2>&1
echo [%date% %time%] scrape end   >> "%LOG%"
