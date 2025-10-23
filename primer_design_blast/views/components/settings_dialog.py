# -*- coding: utf-8 -*-
"""
设置对话框（占位，未来实现）
"""

from PyQt5.QtWidgets import QDialog


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        # TODO: 实现设置界面
