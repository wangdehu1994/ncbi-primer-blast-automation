# -*- coding: utf-8 -*-
"""
可折叠的分组框组件
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, 
    QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QIcon


class CollapsibleBox(QWidget):
    """可折叠的分组框"""
    
    # 折叠状态改变信号
    collapsed_changed = pyqtSignal(bool)
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        
        self.is_collapsed = False
        self.animation_duration = 300
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        self.toggle_button = QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.toggle)
        
        # 标题文本
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: normal;
                color: #000000;
                padding-left: 5px;
            }
        """)
        
        # 标题栏布局
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 6, 8, 6)
        header_layout.addWidget(self.toggle_button)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # 标题栏容器
        self.header_widget = QFrame()
        self.header_widget.setLayout(header_layout)
        self.header_widget.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 0px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                padding: 0;
                min-width: 18px;
                min-height: 18px;
                max-width: 18px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #e5f3ff;
                border-radius: 0px;
            }
        """)
        
        # 内容容器
        self.content_widget = QFrame()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_widget.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-top: none;
                border-radius: 0px;
            }
        """)
        
        # 折叠动画
        self.toggle_animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.toggle_animation.setDuration(self.animation_duration)
        self.toggle_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 添加到主布局
        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.content_widget)
        
        # 更新按钮图标
        self.update_toggle_icon()
    
    def set_title(self, title: str):
        """设置标题"""
        self.title_label.setText(title)
    
    def add_widget(self, widget: QWidget):
        """添加内容组件"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加内容布局"""
        self.content_layout.addLayout(layout)
    
    def toggle(self):
        """切换折叠状态"""
        self.is_collapsed = self.toggle_button.isChecked()
        
        # 记录内容高度
        content_height = self.content_layout.sizeHint().height() + 20
        
        if self.is_collapsed:
            # 折叠
            start_height = self.content_widget.height()
            self.toggle_animation.setStartValue(start_height)
            self.toggle_animation.setEndValue(0)
            # 设置最大高度为0,确保完全隐藏
            self.content_widget.setMaximumHeight(0)
        else:
            # 展开
            self.content_widget.setMaximumHeight(16777215)  # 恢复最大高度
            self.toggle_animation.setStartValue(0)
            self.toggle_animation.setEndValue(content_height)
        
        self.toggle_animation.start()
        self.update_toggle_icon()
        self.collapsed_changed.emit(self.is_collapsed)
    
    def update_toggle_icon(self):
        """更新折叠按钮图标"""
        if self.is_collapsed:
            self.toggle_button.setText("▷")
        else:
            self.toggle_button.setText("▽")
    
    def set_collapsed(self, collapsed: bool):
        """设置折叠状态"""
        if collapsed != self.is_collapsed:
            self.toggle_button.setChecked(collapsed)
            self.toggle()
