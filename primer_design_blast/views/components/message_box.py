# -*- coding: utf-8 -*-
"""
自定义消息框
提供美化的消息提示
"""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt


class CustomMessageBox:
    """自定义消息框类，提供统一的工业风格"""
    
    @staticmethod
    def _create_base_box(parent, icon: QMessageBox.Icon, title: str, message: str, details: str = None):
        msg = QMessageBox(parent)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setDetailedText(details)
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f3f4f6;
                border: 1px solid #e5e7eb;
                min-width: 350px;
            }
            QMessageBox QLabel#qt_msgbox_label { /* 标题文本 */
                color: #111827;
                font-size: 10pt;
            }
            QMessageBox QLabel#qt_msgbox_informativetext { /* 详细信息 */
                color: #4b5563;
            }
            QMessageBox QPushButton {
                background-color: #4f46e5;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 7px 20px;
                font-weight: 600;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4338ca;
            }
            QMessageBox QPushButton:pressed {
                background-color: #3730a3;
            }
            /* 特定按钮样式 */
            QMessageBox QPushButton[text="No"],
            QMessageBox QPushButton[text="Cancel"] {
                background-color: #ffffff;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            QMessageBox QPushButton[text="No"]:hover,
            QMessageBox QPushButton[text="Cancel"]:hover {
                background-color: #f9fafb;
            }
        """)
        return msg

    @staticmethod
    def show_info(parent, title: str, message: str, details: str = None) -> int:
        """显示信息消息"""
        msg = CustomMessageBox._create_base_box(parent, QMessageBox.Information, title, message, details)
        msg.setStandardButtons(QMessageBox.Ok)
        return msg.exec_()
    
    @staticmethod
    def show_warning(parent, title: str, message: str, details: str = None) -> int:
        """显示警告消息"""
        msg = CustomMessageBox._create_base_box(parent, QMessageBox.Warning, title, message, details)
        msg.setStandardButtons(QMessageBox.Ok)
        return msg.exec_()
    
    @staticmethod
    def show_error(parent, title: str, message: str, details: str = None) -> int:
        """显示错误消息"""
        msg = CustomMessageBox._create_base_box(parent, QMessageBox.Critical, title, message, details)
        msg.setStandardButtons(QMessageBox.Ok)
        return msg.exec_()
    
    @staticmethod
    def show_success(parent, title: str, message: str, details: str = None) -> int:
        """显示成功消息"""
        # QMessageBox没有内置的Success图标，使用Information替代
        msg = CustomMessageBox._create_base_box(parent, QMessageBox.Information, title, message, details)
        msg.setStandardButtons(QMessageBox.Ok)
        return msg.exec_()
    
    @staticmethod
    def show_question(parent, title: str, message: str, details: str = None) -> int:
        """显示询问消息"""
        msg = CustomMessageBox._create_base_box(parent, QMessageBox.Question, title, message, details)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        return msg.exec_()
