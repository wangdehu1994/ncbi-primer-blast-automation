# -*- coding: utf-8 -*-
"""
驱动更新对话框
显示浏览器驱动更新进度
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QRadioButton,
    QButtonGroup, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont

from ..services.driver_updater import DriverUpdater


class DriverUpdateWorker(QThread):
    """驱动更新工作线程"""
    
    # 信号
    progress_updated = pyqtSignal(int, int)  # 当前字节数, 总字节数
    message_updated = pyqtSignal(str)  # 消息更新
    finished = pyqtSignal(bool, str)  # 完成信号 (是否成功, 消息)
    
    def __init__(self, browser_type: str):
        """
        Args:
            browser_type: "edge", "chrome", "all"
        """
        super().__init__()
        self.browser_type = browser_type
        self.updater = DriverUpdater()
    
    def progress_callback(self, current: int, total: int):
        """进度回调"""
        self.progress_updated.emit(current, total)
    
    def run(self):
        """执行更新"""
        try:
            if self.browser_type == "edge":
                self.message_updated.emit("正在检测 Edge 浏览器版本...")
                success, msg = self.updater.update_edge_driver(self.progress_callback)
            elif self.browser_type == "chrome":
                self.message_updated.emit("正在检测 Chrome 浏览器版本...")
                success, msg = self.updater.update_chrome_driver(self.progress_callback)
            else:  # all
                self.message_updated.emit("正在检测浏览器版本...")
                success, msg = self.updater.update_all_drivers(self.progress_callback)
            
            self.finished.emit(success, msg)
            
        except Exception as e:
            self.finished.emit(False, f"更新失败: {str(e)}")


class DriverUpdateDialog(QDialog):
    """驱动更新对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("更新浏览器驱动")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 选择浏览器
        browser_group = QGroupBox("选择要更新的浏览器")
        browser_layout = QVBoxLayout()
        
        self.radio_group = QButtonGroup(self)
        
        self.radio_edge = QRadioButton("Microsoft Edge")
        self.radio_chrome = QRadioButton("Google Chrome")
        self.radio_all = QRadioButton("全部更新")
        self.radio_all.setChecked(True)
        
        self.radio_group.addButton(self.radio_edge, 1)
        self.radio_group.addButton(self.radio_chrome, 2)
        self.radio_group.addButton(self.radio_all, 3)
        
        browser_layout.addWidget(self.radio_edge)
        browser_layout.addWidget(self.radio_chrome)
        browser_layout.addWidget(self.radio_all)
        browser_group.setLayout(browser_layout)
        
        layout.addWidget(browser_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        font = QFont("Consolas", 9)
        self.log_text.setFont(font)
        layout.addWidget(self.log_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始更新")
        self.start_button.clicked.connect(self.start_update)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def add_log(self, message: str):
        """添加日志"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def start_update(self):
        """开始更新"""
        # 禁用按钮
        self.start_button.setEnabled(False)
        self.radio_edge.setEnabled(False)
        self.radio_chrome.setEnabled(False)
        self.radio_all.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 清空日志
        self.log_text.clear()
        
        # 确定更新类型
        if self.radio_edge.isChecked():
            browser_type = "edge"
            self.add_log("开始更新 Edge 驱动...")
        elif self.radio_chrome.isChecked():
            browser_type = "chrome"
            self.add_log("开始更新 Chrome 驱动...")
        else:
            browser_type = "all"
            self.add_log("开始更新所有浏览器驱动...")
        
        # 创建工作线程
        self.worker = DriverUpdateWorker(browser_type)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.message_updated.connect(self.on_message_updated)
        self.worker.finished.connect(self.on_update_finished)
        self.worker.start()
    
    def on_progress_updated(self, current: int, total: int):
        """更新进度"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            
            # 更新状态
            current_mb = current / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.status_label.setText(f"下载中... {current_mb:.1f} MB / {total_mb:.1f} MB")
    
    def on_message_updated(self, message: str):
        """更新消息"""
        self.status_label.setText(message)
        self.add_log(message)
    
    def on_update_finished(self, success: bool, message: str):
        """更新完成"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("✅ 更新完成")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("❌ 更新失败")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # 添加详细信息到日志
        self.add_log("=" * 50)
        self.add_log(message)
        self.add_log("=" * 50)
        
        # 启用按钮
        self.start_button.setEnabled(True)
        self.start_button.setText("重新更新")
        self.radio_edge.setEnabled(True)
        self.radio_chrome.setEnabled(True)
        self.radio_all.setEnabled(True)
        
        # 清理线程
        self.worker = None
