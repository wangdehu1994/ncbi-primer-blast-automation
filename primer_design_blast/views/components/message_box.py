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
        msg.setWindowTitle(title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f4f6f8;
                min-width: 380px;
                border: 1px solid #d5d9df;
            }
            QMessageBox QPushButton {
                background-color: #365f9c;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 90px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2d527f;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_warning(parent, title: str, message: str, details: str = None) -> int:
        """显示警告消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #fdf8f3;
                min-width: 380px;
                border: 1px solid #e6d8c7;
            }
            QMessageBox QPushButton {
                background-color: #b4690e;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 90px;
            }
            QMessageBox QPushButton:hover {
                background-color: #98540b;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_error(parent, title: str, message: str, details: str = None) -> int:
        """显示错误消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #fdf4f4;
                min-width: 380px;
                border: 1px solid #ebc8c8;
            }
            QMessageBox QPushButton {
                background-color: #b42318;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 90px;
            }
            QMessageBox QPushButton:hover {
                background-color: #8d1c13;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_success(parent, title: str, message: str, details: str = None) -> int:
        """显示成功消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f3faf3;
                min-width: 380px;
                border: 1px solid #d2e6d2;
            }
            QMessageBox QPushButton {
                background-color: #2f7d3c;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 90px;
            }
            QMessageBox QPushButton:hover {
                background-color: #276a32;
            }
        """)
        return msg.exec_()
    
    @staticmethod
    def show_question(parent, title: str, message: str, details: str = None) -> int:
        """显示询问消息"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(title)
        msg.setText(f"<b>{message}</b>")
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f4f5f7;
                min-width: 380px;
                border: 1px solid #d5d9df;
            }
            QMessageBox QPushButton {
                background-color: #3f4c5d;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 90px;
                margin: 2px;
            }
            QMessageBox QPushButton:hover {
                background-color: #353f4d;
            }
        """)
        return msg.exec_()
