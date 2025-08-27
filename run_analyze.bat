@echo off
chcp 65001 > nul

set PYEXE=C:\Users\shino\AppData\Local\Programs\Python\Python311\python.exe
set WORK=C:\Users\shino\python-tools
set PYTHONUTF8=1

for /f %%a in ('powershell -NoP -C "(Get-Date).ToString(\"yyyyMMdd_HHmmss\")"') do set TS=%%a
set LOG=%WORK%\logs\analyze_%TS%.txt

mkdir "%WORK%\logs" 2>nul
cd /d "%WORK%"

echo [%date% %time%] analyze start >> "%LOG%"
"%PYEXE%" "%WORK%\top_keywords_by_day.py" >> "%LOG%" 2>&1
echo [%date% %time%] analyze end   >> "%LOG%"
