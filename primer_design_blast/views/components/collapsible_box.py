# -*- coding: utf-8 -*-
"""
可折叠的分组框组件
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, 
    QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal


class CollapsibleBox(QWidget):
    """可折叠的分组框"""
    
    # 折叠状态改变信号
    collapsed_changed = pyqtSignal(bool)
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        
        self.is_collapsed = False
        self.animation_duration = 250
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        self.header_widget = QPushButton(title)
        self.header_widget.setCheckable(True)
        self.header_widget.setChecked(False)
        self.header_widget.clicked.connect(self.toggle)
        self.header_widget.setObjectName("collapsible_header")
        
        # 内容容器
        self.content_widget = QFrame()
        self.content_widget.setObjectName("collapsible_content")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 折叠动画
        self.toggle_animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.toggle_animation.setDuration(self.animation_duration)
        self.toggle_animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.content_widget)
        
        self.apply_styles()

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            #collapsible_header {{
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 10px;
                text-align: left;
                font-weight: 600;
                color: #374151;
            }}
            #collapsible_header:hover {{
                background-color: #f9fafb;
            }}
            #collapsible_header:checked {{
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            #collapsible_content {{
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-top: none;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
        """)

    def set_title(self, title: str):
        """设置标题"""
        self.header_widget.setText(title)
    
    def add_widget(self, widget: QWidget):
        """添加内容组件"""
        self.content_layout.addWidget(widget)
        # 添加内容后，确保内容区域有足够的高度和正确的尺寸策略
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.content_widget.setMinimumHeight(1)  # 避免 sizeHint=0
        self.content_widget.adjustSize()
        self.content_widget.setMaximumHeight(16777215)
    
    def add_layout(self, layout):
        """添加内容布局"""
        self.content_layout.addLayout(layout)
        # 添加内容后，确保内容区域有足够的高度和正确的尺寸策略
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.content_widget.setMinimumHeight(1)  # 避免 sizeHint=0
        self.content_widget.adjustSize()
        self.content_widget.setMaximumHeight(16777215)
    
    def toggle(self):
        """切换折叠状态"""
        self.is_collapsed = self.header_widget.isChecked()
        
        # 获取内容的实际高度（兜底避免0）
        content_height = max(self.content_widget.sizeHint().height(), 1)
        
        if self.is_collapsed:
            # 折叠：从当前高度缩小到0
            self.toggle_animation.setStartValue(self.content_widget.height())
            self.toggle_animation.setEndValue(0)
        else:
            # 展开：先设置一个足够大的最大高度，然后动画到实际高度
            self.content_widget.setMaximumHeight(16777215)
            self.toggle_animation.setStartValue(0)
            self.toggle_animation.setEndValue(content_height)
        
        self.toggle_animation.start()
        
        # 动画结束后，如果是展开状态，移除最大高度限制
        if not self.is_collapsed:
            try:
                self.toggle_animation.finished.disconnect(self._on_expand_finished)
            except Exception:
                pass
            self.toggle_animation.finished.connect(self._on_expand_finished)
        
        self.collapsed_changed.emit(self.is_collapsed)
    
    def _on_expand_finished(self):
        """展开动画完成后，移除高度限制并通知父窗口重算几何"""
        self.content_widget.setMaximumHeight(16777215)
        # 通知父窗口重算几何
        parent_win = self.window()
        if parent_win:
            try:
                parent_win.adjustSize()
            except Exception:
                pass
        try:
            self.toggle_animation.finished.disconnect(self._on_expand_finished)
        except Exception:
            pass

    def set_collapsed(self, collapsed: bool):
        """设置折叠状态"""
        if collapsed != self.is_collapsed:
            self.header_widget.setChecked(collapsed)
            self.toggle()
