@echo off
set "PYEXE=C:\Users\shino\AppData\Local\Programs\Python\Python311\python.exe"
set "WORK=C:\Users\shino\python-tools"
cd /d "%WORK%"

rem ここで必ずログを作る（Pythonが失敗しても痕跡が残る）
echo [%date% %time%] analyze start >> "%WORK%\analyze_log.txt"

"%PYEXE%" "%WORK%\top_keywords_by_day.py" >> "%WORK%\analyze_log.txt" 2>&1

echo [%date% %time%] analyze end   >> "%WORK%\analyze_log.txt"
