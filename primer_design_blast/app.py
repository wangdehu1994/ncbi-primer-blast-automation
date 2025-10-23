# -*- coding: utf-8 -*-
"""
引物设计套件 - 主程序入口
Primer Design Suite v3.0

一个专业的NCBI Primer-BLAST自动化工具
"""

import sys
import logging
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from .views.main_window import MainWindow
from .utils.logger import setup_logger
from .utils.resource_utils import get_resource_path
from .models.config import AppConfig


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger("primer_design_blast", logging.INFO)
    logger.info("=" * 60)
    logger.info("引物设计套件启动")
    logger.info("=" * 60)
    
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用信息
    config = AppConfig()
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName("生物信息学工具")
    
    # 设置应用图标
    icon_path = get_resource_path("resources/icon.ico")
    if Path(icon_path).exists():
        app.setWindowIcon(QIcon(icon_path))
        logger.info(f"已加载应用图标: {icon_path}")
    else:
        logger.warning(f"未找到应用图标: {icon_path}")
    
    # 设置全局字体
    from PyQt5.QtGui import QFont
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)
    
    try:
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        logger.info("主窗口已显示")
        logger.info("应用程序就绪")
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"程序运行错误: {e}", exc_info=True)
        
        # 显示错误对话框
        from PyQt5.QtWidgets import QMessageBox
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("启动错误")
        error_msg.setText(f"程序启动失败:\n{str(e)}")
        error_msg.setStandardButtons(QMessageBox.Ok)
        error_msg.exec_()
        
        sys.exit(1)


if __name__ == "__main__":
    main()
