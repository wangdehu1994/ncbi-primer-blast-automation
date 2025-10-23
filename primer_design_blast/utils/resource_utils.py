# -*- coding: utf-8 -*-
"""
资源文件路径工具
支持PyInstaller打包后的exe访问资源文件
"""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径，支持打包后的exe
    
    Args:
        relative_path: 相对路径，例如:
            - "resources/icon.ico"
            - "resources/hg19ToHg38/hg19ToHg38.over.chain"
            - "resources/drivers/win10/msedgedriver.exe"
        
    Returns:
        绝对路径
    """
    try:
        # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境：定位到primer_design_suite目录
        # 当前文件: primer_design_suite/utils/resource_utils.py
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)
