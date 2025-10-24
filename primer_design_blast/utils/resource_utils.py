# -*- coding: utf-8 -*-
"""
资源文件路径工具
支持PyInstaller打包后的exe访问资源文件，以及Inno Setup安装包模式
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str, writable: bool = False) -> str:
    """
    获取资源文件的绝对路径，支持开发环境和安装包模式
    
    Args:
        relative_path: 相对路径，例如:
            - "resources/icon.ico"
            - "resources/hg19ToHg38/hg19ToHg38.over.chain"
            - "resources/drivers/msedgedriver.exe"
        writable: 是否需要可写入（如驱动文件下载），默认False
        
    Returns:
        绝对路径
    
    说明:
        - 开发环境: 使用源代码目录
        - 安装包模式: 只读资源使用安装目录，可写资源使用用户数据目录
    """
    # 判断是否为安装包模式（通过检查是否在Program Files下，且不是python.exe）
    exe_path = sys.executable
    exe_name = os.path.basename(exe_path).lower()
    is_installed = (
        exe_name != 'python.exe' and
        exe_name != 'pythonw.exe' and
        ('Program Files' in exe_path or 'Program Files (x86)' in exe_path)
    )
    
    # 安装包模式下，如果需要可写路径，使用用户数据目录
    if writable and is_installed:
        # 使用 %LOCALAPPDATA%\PrimerDesignBlast 存储可写数据
        app_data = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
        base_path = os.path.join(app_data, 'PrimerDesignBlast')
        
        # 确保目录存在
        full_path = os.path.join(base_path, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        return full_path
    
    # 只读资源：使用程序所在目录
    if hasattr(sys, 'frozen'):
        # PyInstaller 打包后（frozen状态）
        # sys.executable 是打包后的 exe 路径（如 dist/PrimerDesignBlast/引物设计工具.exe）
        # 资源文件在 dist/PrimerDesignBlast/ 目录下
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境：定位到项目根目录（包含 primer_design_blast 包的目录）
        # 当前文件: primer_design_blast/utils/resource_utils.py
        # 向上两级到 primer_design_blast 包目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def get_driver_path(driver_name: str) -> str:
    """
    获取浏览器驱动路径（专用函数，处理可写需求）
    
    Args:
        driver_name: 驱动文件名，如 "msedgedriver.exe" 或 "chromedriver.exe"
        
    Returns:
        驱动文件的绝对路径
    """
    relative_path = f"resources/drivers/{driver_name}"
    
    # 首先检查可写位置（用户数据目录）是否有驱动
    writable_path = get_resource_path(relative_path, writable=True)
    if os.path.exists(writable_path):
        return writable_path
    
    # 否则使用安装目录的驱动（如果存在）
    installed_path = get_resource_path(relative_path, writable=False)
    if os.path.exists(installed_path):
        # 对于安装包模式，首次使用时复制到可写位置
        exe_path = sys.executable
        exe_name = os.path.basename(exe_path).lower()
        is_installed = (
            exe_name != 'python.exe' and
            exe_name != 'pythonw.exe' and
            ('Program Files' in exe_path or 'Program Files (x86)' in exe_path)
        )
        
        if is_installed:
            # 复制到可写位置
            import shutil
            os.makedirs(os.path.dirname(writable_path), exist_ok=True)
            shutil.copy2(installed_path, writable_path)
            return writable_path
        
        return installed_path
    
    # 都不存在，返回可写位置（便于后续下载）
    return writable_path
