@echo off
chcp 65001 >nul
REM ============================================
REM 引物设计工具 - 自动打包脚本
REM 功能：自动执行 PyInstaller 打包 + Inno Setup 安装包生成
REM 适用于 Windows 7/8/10/11
REM ============================================

echo.
echo ================================================
echo    引物设计工具 - 自动打包脚本 v3.0
echo ================================================
echo.

REM 设置颜色
color 0A

REM 获取脚本所在目录
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [1/5] 检查环境...
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！请先安装 Python 3.8+
    pause
    exit /b 1
)
echo [√] Python 已安装

REM 检查 PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [!] 未检测到 PyInstaller，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败！
        pause
        exit /b 1
    )
)
echo [√] PyInstaller 已就绪

REM 检查 Inno Setup（可选）
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_PATH%" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)
if not exist "%INNO_PATH%" (
    echo [!] 未检测到 Inno Setup，仅执行 PyInstaller 打包
    set SKIP_INNO=1
) else (
    echo [√] Inno Setup 已就绪
    set SKIP_INNO=0
)

echo.
echo [2/5] 清理旧文件...
echo.

REM 清理旧的打包文件
if exist "build" (
    echo 正在删除 build 目录...
    rmdir /s /q "build"
)
if exist "dist" (
    echo 正在删除 dist 目录...
    rmdir /s /q "dist"
)
if exist "installer_output" (
    echo 正在删除 installer_output 目录...
    rmdir /s /q "installer_output"
)

echo [√] 清理完成

echo.
echo [3/5] 执行 PyInstaller 打包...
echo.

REM 执行打包
pyinstaller build.spec

if errorlevel 1 (
    echo.
    echo [错误] PyInstaller 打包失败！
    pause
    exit /b 1
)

echo.
echo [√] PyInstaller 打包完成！
echo    输出目录: dist\PrimerDesignBlast

REM 如果跳过 Inno Setup
if "%SKIP_INNO%"=="1" (
    echo.
    echo [提示] 未安装 Inno Setup，跳过安装包生成
    echo        您可以手动分发 dist\PrimerDesignBlast 文件夹
    echo.
    echo ================================================
    echo    打包完成！
    echo ================================================
    pause
    exit /b 0
)

echo.
echo [4/5] 生成 Inno Setup 安装包...
echo.

REM 生成安装包
"%INNO_PATH%" "setup.iss"

if errorlevel 1 (
    echo.
    echo [错误] Inno Setup 安装包生成失败！
    pause
    exit /b 1
)

echo.
echo [√] 安装包生成完成！

echo.
echo [5/5] 打包结果汇总...
echo.

REM 显示结果
echo ================================================
echo    打包完成！
echo ================================================
echo.
echo 生成的文件：
echo.
echo 1. PyInstaller 打包输出:
echo    目录: dist\PrimerDesignBlast\
echo    主程序: dist\PrimerDesignBlast\引物设计工具.exe
echo.
echo 2. Inno Setup 安装包:
dir /b installer_output\*.exe 2>nul
if errorlevel 1 (
    echo    [未生成]
) else (
    for %%f in (installer_output\*.exe) do (
        echo    文件: %%f
        echo    大小: 
        dir "%%f" | find "%%~nxf"
    )
)
echo.
echo ================================================
echo.
echo 下一步：
echo 1. 测试安装包: 运行 installer_output\*.exe
echo 2. 测试程序: 运行 dist\PrimerDesignBlast\引物设计工具.exe
echo 3. 分发安装包给用户
echo.
echo ================================================

REM 询问是否打开输出目录
echo.
set /p OPEN_DIR="是否打开输出目录？(Y/N): "
if /i "%OPEN_DIR%"=="Y" (
    start explorer "installer_output"
)

echo.
pause
