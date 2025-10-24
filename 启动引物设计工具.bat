@echo off
chcp 65001 >nul
echo ========================================
echo   引物设计工具 v3.0 启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [信息] Python环境检测通过
echo.

REM 进入程序目录
cd /d "%~dp0"

echo [信息] 正在启动程序...
echo.

REM 运行程序
python run.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错，请查看错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo [信息] 程序已关闭
pause
