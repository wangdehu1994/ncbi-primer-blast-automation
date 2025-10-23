# -*- coding: utf-8 -*-
"""
模板管理对话框（占位，未来实现）
"""

from PyQt5.QtWidgets import QDialog


class TemplateDialog(QDialog):
    """模板管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("模板管理")
        # TODO: 实现模板管理界面
