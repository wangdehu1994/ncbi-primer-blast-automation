# -*- coding: utf-8 -*-
"""
坐标转换文件下载对话框
用于下载 hg19ToHg38.over.chain 文件
"""

import os
import gzip
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


class ChainFileDownloadWorker(QThread):
    """坐标转换文件下载工作线程"""
    
    # 信号
    progress_updated = pyqtSignal(int, int)  # 当前字节数, 总字节数
    message_updated = pyqtSignal(str)  # 消息更新
    finished = pyqtSignal(bool, str)  # 完成信号 (是否成功, 消息)
    
    # UCSC 下载地址
    DOWNLOAD_URL = "https://hgdownload.cse.ucsc.edu/goldenpath/hg19/liftOver/hg19ToHg38.over.chain.gz"
    
    def __init__(self, target_dir: str):
        """
        Args:
            target_dir: 目标目录路径
        """
        super().__init__()
        self.target_dir = Path(target_dir)
        self.gz_file = self.target_dir / "hg19ToHg38.over.chain.gz"
        self.chain_file = self.target_dir / "hg19ToHg38.over.chain"
    
    def download_file(self):
        """下载文件"""
        if not HAS_URLLIB:
            raise ImportError("urllib 模块不可用")
        
        # 确保目标目录存在
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        self.message_updated.emit(f"正在连接服务器...\n{self.DOWNLOAD_URL}")
        
        # 下载文件
        def reporthook(block_num, block_size, total_size):
            """下载进度回调"""
            downloaded = block_num * block_size
            if total_size > 0:
                self.progress_updated.emit(downloaded, total_size)
        
        try:
            urllib.request.urlretrieve(
                self.DOWNLOAD_URL, 
                str(self.gz_file),
                reporthook=reporthook
            )
            return True
        except urllib.error.URLError as e:
            raise Exception(f"下载失败: {str(e)}")
    
    def decompress_file(self):
        """解压文件"""
        self.message_updated.emit("正在解压文件...")
        
        try:
            with gzip.open(str(self.gz_file), 'rb') as f_in:
                with open(str(self.chain_file), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除压缩文件
            if self.gz_file.exists():
                self.gz_file.unlink()
                
            return True
        except Exception as e:
            raise Exception(f"解压失败: {str(e)}")
    
    def run(self):
        """执行下载和解压"""
        try:
            # 检查文件是否已存在
            if self.chain_file.exists():
                file_size = self.chain_file.stat().st_size / (1024 * 1024)  # MB
                self.message_updated.emit(
                    f"文件已存在!\n"
                    f"位置: {self.chain_file}\n"
                    f"大小: {file_size:.2f} MB\n\n"
                    f"如需重新下载，请先手动删除该文件。"
                )
                self.finished.emit(True, "文件已存在，无需重复下载")
                return
            
            # 下载文件
            self.message_updated.emit("开始下载坐标转换文件...")
            self.download_file()
            
            file_size = self.gz_file.stat().st_size / (1024 * 1024)  # MB
            self.message_updated.emit(f"下载完成! 文件大小: {file_size:.2f} MB")
            
            # 解压文件
            self.decompress_file()
            
            final_size = self.chain_file.stat().st_size / (1024 * 1024)  # MB
            self.message_updated.emit(
                f"解压完成!\n"
                f"文件位置: {self.chain_file}\n"
                f"文件大小: {final_size:.2f} MB\n\n"
                f"现在可以使用 hg19→hg38 坐标转换功能了!"
            )
            
            self.finished.emit(True, "下载并安装成功!")
            
        except Exception as e:
            error_msg = str(e)
            self.message_updated.emit(f"\n❌ 错误: {error_msg}")
            self.finished.emit(False, f"操作失败: {error_msg}")


class ChainFileDownloadDialog(QDialog):
    """坐标转换文件下载对话框"""
    
    def __init__(self, target_dir: str, parent=None):
        """
        Args:
            target_dir: 目标目录路径
            parent: 父窗口
        """
        super().__init__(parent)
        self.target_dir = target_dir
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("下载坐标转换文件")
        self.setModal(True)
        self.setMinimumWidth(550)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 说明信息
        info_group = QGroupBox("文件说明")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel(
            "此工具将从 UCSC 官方网站下载 hg19ToHg38.over.chain 文件\n\n"
            "• 文件用途: 将 hg19/GRCh37 坐标转换为 hg38/GRCh38\n"
            "• 文件大小: 约 1.5 MB (解压后)\n"
            "• 下载来源: UCSC Genome Browser (官方可信源)\n\n"
            "如果您的输入坐标已经是 hg38 版本，则不需要此文件。"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #4b5563; padding: 5px;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # 状态标签
        self.status_label = QLabel("准备下载")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: 600; color: #374151;")
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日志文本框
        log_label = QLabel("下载日志:")
        log_label.setStyleSheet("font-weight: 600; color: #374151; margin-top: 5px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("log_display")
        self.log_text.setMinimumHeight(150)
        layout.addWidget(self.log_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("开始下载")
        self.start_button.setObjectName("primary_button")
        self.start_button.clicked.connect(self.start_download)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.apply_styles()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f4f6;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px;
                font-weight: 600;
                color: #374151;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px;
                margin-left: 10px;
            }
            QProgressBar {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                text-align: center;
                background-color: #e5e7eb;
                color: #4b5563;
                font-weight: 600;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 3px;
            }
            QTextEdit#log_display {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                background-color: #f9fafb;
                color: #374151;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                color: #374151;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
            QPushButton:disabled {
                background-color: #f3f4f6;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
            QPushButton#primary_button {
                background-color: #10b981;
                color: white;
                border: none;
            }
            QPushButton#primary_button:hover {
                background-color: #059669;
            }
            QPushButton#primary_button:disabled {
                background-color: #9ca3af;
            }
        """)
    
    def start_download(self):
        """开始下载"""
        if self.worker and self.worker.isRunning():
            return
        
        # 禁用开始按钮
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("下载中...")
        self.log_text.clear()
        
        # 创建工作线程
        self.worker = ChainFileDownloadWorker(self.target_dir)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.message_updated.connect(self.on_message_updated)
        self.worker.finished.connect(self.on_finished)
        
        # 启动下载
        self.worker.start()
    
    def on_progress_updated(self, current: int, total: int):
        """更新进度"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            
            # 格式化大小显示
            current_mb = current / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.status_label.setText(f"下载中: {current_mb:.2f} MB / {total_mb:.2f} MB ({percent}%)")
    
    def on_message_updated(self, message: str):
        """更新消息"""
        self.log_text.append(message)
    
    def on_finished(self, success: bool, message: str):
        """下载完成"""
        self.start_button.setEnabled(True)
        
        if success:
            self.status_label.setText("✅ 完成")
            self.status_label.setStyleSheet("font-weight: 600; color: #10b981;")
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText("❌ 失败")
            self.status_label.setStyleSheet("font-weight: 600; color: #ef4444;")
        
        self.log_text.append(f"\n{'='*50}")
        self.log_text.append(f"{'✅ 成功' if success else '❌ 失败'}: {message}")
        self.log_text.append(f"{'='*50}")
