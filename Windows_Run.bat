@echo off
setlocal

:: 设置环境变量
set ENV_NAME=gpt
set ENV_PATH=%~dp0%ENV_NAME%
set SCRIPT_PATH=%~dp0main.py

:: 判断环境是否已解压
if not exist "%ENV_PATH%" (
    echo Extracting environment...
    mkdir "%ENV_PATH%"
    tar -xzf gpt.tar.gz -C "%ENV_PATH%"
    
    :: 运行conda环境激活脚本
    call "%ENV_PATH%\Scripts\activate.bat"
) else (
    :: 如果环境已存在,直接激活
    call "%ENV_PATH%\Scripts\activate.bat"
)
echo Start to run program:
:: 运行Python脚本
python "%SCRIPT_PATH%"

endlocal
pause