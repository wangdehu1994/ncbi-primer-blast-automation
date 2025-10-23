# -*- coding: utf-8 -*-
"""
日志配置工具
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "primer_design_suite",
    level: int = logging.INFO,
    log_to_file: bool = True
) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        name: 日志器名称
        level: 日志级别
        log_to_file: 是否输出到文件
        
    Returns:
        配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件输出
    if log_to_file:
        # 创建日志目录
        log_dir = Path.home() / '.primer_design_suite' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 按日期命名日志文件
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
