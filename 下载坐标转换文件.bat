@echo off
chcp 65001 >nul
echo ========================================
echo 下载 hg19ToHg38 坐标转换文件
echo ========================================
echo.

set "DOWNLOAD_URL=https://hgdownload.cse.ucsc.edu/goldenpath/hg19/liftOver/hg19ToHg38.over.chain.gz"
set "TARGET_DIR=%~dp0primer_design_blast\resources\hg19ToHg38"
set "GZ_FILE=%TARGET_DIR%\hg19ToHg38.over.chain.gz"
set "CHAIN_FILE=%TARGET_DIR%\hg19ToHg38.over.chain"

echo 目标目录: %TARGET_DIR%
echo.

REM 检查目录是否存在
if not exist "%TARGET_DIR%" (
    echo [错误] 目标目录不存在: %TARGET_DIR%
    echo 请确保在正确的位置运行此脚本
    pause
    exit /b 1
)

REM 检查文件是否已存在
if exist "%CHAIN_FILE%" (
    echo [提示] 文件已存在: %CHAIN_FILE%
    set /p "CONFIRM=是否重新下载？(Y/N): "
    if /i not "%CONFIRM%"=="Y" (
        echo 已取消下载
        pause
        exit /b 0
    )
)

echo 正在下载文件...
echo 下载地址: %DOWNLOAD_URL%
echo.

REM 使用 PowerShell 下载文件
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { $ProgressPreference = 'SilentlyContinue'; Write-Host '开始下载...'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%GZ_FILE%' -UseBasicParsing; Write-Host '下载完成！' } catch { Write-Host '[错误] 下载失败: ' $_.Exception.Message; exit 1 }}"

if not exist "%GZ_FILE%" (
    echo.
    echo [错误] 下载失败！
    echo.
    echo 可能的原因：
    echo 1. 网络连接问题
    echo 2. UCSC 服务器暂时不可用
    echo.
    echo 请尝试：
    echo 1. 检查网络连接
    echo 2. 手动访问下载链接：%DOWNLOAD_URL%
    echo 3. 查看详细说明：primer_design_blast\resources\hg19ToHg38\README.md
    pause
    exit /b 1
)

echo.
echo ========================================
echo 文件下载成功！
echo ========================================
echo.
echo 下载的文件: %GZ_FILE%
echo 文件大小: 
powershell -Command "& {$size = (Get-Item '%GZ_FILE%').Length / 1MB; Write-Host ('{0:N2} MB' -f $size)}"
echo.

echo 正在解压文件...
echo.

REM 检查是否安装了 7-Zip
set "SEVENZIP_PATH=C:\Program Files\7-Zip\7z.exe"
if exist "%SEVENZIP_PATH%" (
    echo 使用 7-Zip 解压...
    "%SEVENZIP_PATH%" e "%GZ_FILE%" -o"%TARGET_DIR%" -y
    if exist "%CHAIN_FILE%" (
        echo 解压成功！
        del "%GZ_FILE%"
        goto :success
    )
)

REM 尝试使用 PowerShell 解压（Windows 10+）
echo 使用 PowerShell 解压...
powershell -Command "& {try { Add-Type -AssemblyName System.IO.Compression.FileSystem; $gzFile = '%GZ_FILE%'; $outFile = '%CHAIN_FILE%'; $gzStream = New-Object System.IO.FileStream($gzFile, [System.IO.FileMode]::Open); $gzipStream = New-Object System.IO.Compression.GzipStream($gzStream, [System.IO.Compression.CompressionMode]::Decompress); $outStream = New-Object System.IO.FileStream($outFile, [System.IO.FileMode]::Create); $gzipStream.CopyTo($outStream); $outStream.Close(); $gzipStream.Close(); $gzStream.Close(); Write-Host '解压成功！' } catch { Write-Host '[错误] 解压失败: ' $_.Exception.Message; exit 1 }}"

if exist "%CHAIN_FILE%" (
    echo 解压成功！
    del "%GZ_FILE%"
    goto :success
) else (
    echo.
    echo [提示] 自动解压失败
    echo.
    echo 请手动解压文件：
    echo 1. 找到下载的文件：%GZ_FILE%
    echo 2. 使用解压软件（如 7-Zip、WinRAR）解压
    echo 3. 将解压后的文件放到：%TARGET_DIR%
    echo 4. 确保文件名为：hg19ToHg38.over.chain
    echo.
    pause
    exit /b 1
)

:success
echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 文件位置: %CHAIN_FILE%
echo 文件大小:
powershell -Command "& {$size = (Get-Item '%CHAIN_FILE%').Length / 1MB; Write-Host ('{0:N2} MB' -f $size)}"
echo.
echo 现在可以使用 hg19→hg38 坐标转换功能了！
echo.
pause
