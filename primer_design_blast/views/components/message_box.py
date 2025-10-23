# -*- coding: utf-8 -*-
"""
自定义消息框
提供美化的消息提示
"""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt


class CustomMessageBox:
    """自定义消息框类"""
    
    @staticmethod
    def show_info(parent, title: str, message: str, details: str = None) -> int:
        """显示信息消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("💡 " + title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0f8ff;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_warning(parent, title: str, message: str, details: str = None) -> int:
        """显示警告消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("⚠️ " + title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #fffbf0;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_error(parent, title: str, message: str, details: str = None) -> int:
        """显示错误消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("❌ " + title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #fff5f5;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_success(parent, title: str, message: str, details: str = None) -> int:
        """显示成功消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("✅ " + title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0fff4;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #229954;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_question(parent, title: str, message: str, details: str = None) -> int:
        """显示询问消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("❓ " + title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
                margin: 2px;
            }
            QMessageBox QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        return msg.exec_()
