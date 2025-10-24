# -*- coding: utf-8 -*-
"""
主窗口UI
包含菜单栏、工具栏、参数模板管理等功能
"""

import os
import sys
import threading
import logging
from typing import Optional
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QGroupBox, QFormLayout, QPlainTextEdit,
    QProgressBar, QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
    QInputDialog, QDialog, QDialogButtonBox, QTextEdit, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QTextCursor

from ..models.primer_params import PrimerParams
from ..models.config import AppConfig, TemplateManager
from ..controllers.primer_controller import PrimerController, ProcessingStats
from ..utils.resource_utils import get_resource_path
from .components.message_box import CustomMessageBox
from .components.template_dialog import TemplateDialog
from .components.driver_update_dialog import DriverUpdateDialog
from .components.chain_file_download_dialog import ChainFileDownloadDialog
from .components.parameter_dialog import ParameterDialog


class WorkerThread(QThread):
    """后台工作线程"""
    
    def __init__(self, controller: PrimerController, *args, **kwargs):
        super().__init__()
        self.controller = controller
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """执行批量处理"""
        self.controller.start_batch_processing(*self.args, **self.kwargs)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        self.template_manager = TemplateManager()
        self.controller = PrimerController()
        self.worker_thread = None
        
        # 当前参数
        self.current_params = PrimerParams()
        
        # 初始化UI
        self.init_ui()
        self.setup_connections()
        
        # 加载默认参数
        self.load_default_params()
        
        self.logger.info("主窗口初始化完成")
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{self.config.APP_NAME} v{self.config.APP_VERSION}")
        # 初始大小
        self.setGeometry(100, 100, 900, 750)
        # 设置最小尺寸
        self.setMinimumSize(850, 600)
        
        # 设置图标
        icon_path = get_resource_path("resources/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 设置中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # 创建各个区域
        main_layout.addWidget(self.create_input_area())
        main_layout.addWidget(self.create_progress_area())
        main_layout.addWidget(self.create_control_buttons())

        # 应用样式
        self.apply_styles()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        import_action = QAction("导入坐标文件...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.triggered.connect(self.import_coordinates)
        file_menu.addAction(import_action)

        export_action = QAction("导出当前坐标...", self)
        export_action.setShortcut("Ctrl+S")
        export_action.triggered.connect(self.export_coordinates)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        clear_action = QAction("清空输入", self)
        clear_action.setShortcut("Ctrl+D")
        clear_action.triggered.connect(self.clear_input)
        edit_menu.addAction(clear_action)

        validate_action = QAction("验证坐标", self)
        validate_action.setShortcut("Ctrl+V")
        validate_action.triggered.connect(self.validate_coordinates)
        edit_menu.addAction(validate_action)

        # 模板菜单
        template_menu = menubar.addMenu("模板(&T)")

        save_template_action = QAction("保存当前参数为模板...", self)
        save_template_action.triggered.connect(lambda: self.open_parameter_dialog(action='save'))
        template_menu.addAction(save_template_action)

        load_template_action = QAction("加载参数模板...", self)
        load_template_action.triggered.connect(lambda: self.open_parameter_dialog(action='load'))
        template_menu.addAction(load_template_action)

        manage_template_action = QAction("管理模板...", self)
        manage_template_action.triggered.connect(self.manage_templates)
        template_menu.addAction(manage_template_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&G)")

        driver_update_action = QAction("更新浏览器驱动...", self)
        driver_update_action.triggered.connect(self.update_driver)
        tools_menu.addAction(driver_update_action)

        chain_file_download_action = QAction("下载坐标转换文件...", self)
        chain_file_download_action.triggered.connect(self.download_chain_file)
        tools_menu.addAction(chain_file_download_action)

        tools_menu.addSeparator()

        close_browser_action = QAction("关闭浏览器", self)
        close_browser_action.triggered.connect(self.close_browser)
        tools_menu.addAction(close_browser_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        usage_action = QAction("使用说明", self)
        usage_action.setShortcut("F1")
        usage_action.triggered.connect(self.show_usage)
        help_menu.addAction(usage_action)

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_input_area(self) -> QGroupBox:
        """创建输入区域"""
        group = QGroupBox("1. 核心输入")

        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft)
        layout.setFormAlignment(Qt.AlignLeft)
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(12)
        layout.setContentsMargins(15, 20, 15, 15)

        # 多行输入
        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText(
            "请输入染色体坐标，每行一组，格式：chr1 123456\n"
            "支持1-22号染色体及X、Y。可直接粘贴多行数据。"
        )
        self.input_text.setMinimumHeight(120)
        self.input_text.setMaximumHeight(180)
        self.input_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        layout.addRow("批量坐标:", self.input_text)
        
        # 基因组版本和浏览器
        options_layout = QHBoxLayout()
        options_layout.setSpacing(10)
        
        self.version_combo = QComboBox()
        self.version_combo.addItems(["hg19/GRCh37","hg38/GRCh38"])
        
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Edge", "Chrome"])
        
        options_layout.addWidget(self.version_combo)
        options_layout.addWidget(self.browser_combo)
        options_layout.addStretch()
        
        layout.addRow("版本/浏览器:", options_layout)
        
        group.setLayout(layout)
        return group
    
    def open_parameter_dialog(self, action: str = None):
        """打开引物参数设置对话框
        
        Args:
            action: 打开后执行的操作，可选值：'save'(保存模板), 'load'(加载模板), None(正常打开)
        """
        dialog = ParameterDialog(self.current_params, self)
        
        # 根据 action 执行对应操作
        if action == 'save':
            dialog.save_template()
        elif action == 'load':
            dialog.load_template()
            
        if dialog.exec_() == QDialog.Accepted:
            params = dialog.get_params()
            if params:
                self.current_params = params
                self._add_progress_message(f"参数已更新", "⚙️")
    
    def create_control_buttons(self) -> QWidget:
        """创建控制按钮区域"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(15)

        # 参数设置按钮
        self.param_button = QPushButton("⚙️ 参数设置")
        self.param_button.clicked.connect(self.open_parameter_dialog)
        self.param_button.setMinimumHeight(36)

        self.start_button = QPushButton("▶ 开始处理")
        # 移除SVG图标引用，使用文本符号代替
        self.start_button.setObjectName("startButton")
        self.start_button.setMinimumHeight(36)

        self.stop_button = QPushButton("⏹ 停止处理")
        # 移除SVG图标引用，使用文本符号代替
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setMinimumHeight(36)
        self.stop_button.setEnabled(False)

        layout.addStretch()
        layout.addWidget(self.param_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addStretch()

        return widget
    
    def create_progress_area(self) -> QGroupBox:
        """创建进度显示区域"""
        group = QGroupBox("2. 运行日志")

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)

        # 统计信息和进度条
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)
        
        self.stats_label = QLabel("就绪")
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMaximumWidth(200)
        
        progress_layout.addWidget(self.stats_label)
        progress_layout.addStretch()
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)
        
        # 日志显示
        self.progress_display = QPlainTextEdit()
        self.progress_display.setReadOnly(True)
        self.progress_display.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.progress_display.setMaximumBlockCount(500)
        self.progress_display.setMinimumHeight(120)  # 从200调小，给参数区让路
        layout.addWidget(self.progress_display)
        
        # 允许父布局管理高度
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        group.setLayout(layout)
        return group

    def apply_styles(self):
        """应用QSS样式"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.config.COLOR_BASE};
            }}

            QWidget {{
                font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
                font-size: 9pt;
                color: #1f2937; /* 深灰色文字 */
            }}

            /* 菜单栏 */
            QMenuBar {{
                background-color: #ffffff;
                border-bottom: 1px solid #e5e7eb;
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 6px 12px;
                background: transparent;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: #e5e7eb;
            }}
            QMenu {{
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px;
                border-radius: 3px;
            }}
            QMenu::item:selected {{
                background-color: #4f46e5; /* 强调色 */
                color: #ffffff;
            }}
            QMenu::separator {{
                height: 1px;
                background: #e5e7eb;
                margin: 4px 8px;
            }}

            /* 分组框 */
            QGroupBox {{
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                margin-left: 10px;
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
                color: #374151;
            }}

            /* 输入框和文本域 */
            QLineEdit, QPlainTextEdit, QComboBox {{
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 9pt;
                color: #1f2937;
            }}
            QLineEdit:hover, QPlainTextEdit:hover, QComboBox:hover {{
                border-color: #9ca3af;
            }}
            QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
                border-color: #4f46e5;
                outline: none;
            }}
            QLineEdit {{
                min-height: 20px;
            }}
            QPlainTextEdit {{
                background-color: #f9fafb;
            }}

            /* 下拉框 */
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #d1d5db;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }}
            QComboBox::down-arrow {{
                /* 移除SVG图标引用，使用系统默认箭头 */
                width: 14px;
                height: 14px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                selection-background-color: #e0e7ff;
                selection-color: #374151;
                padding: 2px;
            }}

            /* 按钮 */
            QPushButton {{
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 7px 15px;
                font-weight: 600;
                color: #374151;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background-color: #f9fafb;
                border-color: #9ca3af;
            }}
            QPushButton:pressed {{
                background-color: #f3f4f6;
            }}
            QPushButton:disabled {{
                background-color: #f3f4f6;
                color: #9ca3af;
                border-color: #e5e7eb;
            }}

            /* 主按钮 (开始) */
            QPushButton#startButton {{
                background-color: {self.config.COLOR_ACCENT};
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 16px;
            }}
            QPushButton#startButton:hover {{
                background-color: {self.config.COLOR_ACCENT_HOVER};
            }}
            QPushButton#startButton:pressed {{
                background-color: {self.config.COLOR_ACCENT_PRESSED};
            }}

            /* 危险按钮 (停止) */
            QPushButton#stopButton {{
                background-color: #dc2626; /* red-600 */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 16px;
            }}
            QPushButton#stopButton:hover {{
                background-color: #b91c1c; /* red-700 */
            }}
            QPushButton#stopButton:pressed {{
                background-color: #991b1b; /* red-800 */
            }}
            
            QPushButton#stopButton:disabled {{
                background-color: #fca5a5; /* red-300 */
                color: #fef2f2; /* red-50 */
            }}

            /* 按钮图标 */
            QPushButton > QIcon {{
                color: #ffffff;
            }}

            /* 进度条 */
            QProgressBar {{
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                text-align: center;
                background-color: #e5e7eb;
                color: #4b5563;
                font-weight: 600;
            }}
            QProgressBar::chunk {{
                background-color: #4f46e5;
                border-radius: 3px;
            }}
            
            /* 标签 */
            QLabel {{
                color: #374151;
            }}
            
            /* 日志区域 */
            #log_display {{
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                background-color: #f9fafb;
                color: #374151;
                border: 1px solid #e5e7eb;
            }}
        """)
    
    def setup_connections(self):
        """设置信号连接"""
        # 控制器信号连接
        self.controller.progress_updated.connect(self.on_progress_updated)
        self.controller.stats_updated.connect(self.on_stats_updated)
        self.controller.task_started.connect(self.on_task_started)
        self.controller.task_completed.connect(self.on_task_completed)
        self.controller.task_stopped.connect(self.on_task_stopped)
        self.controller.error_occurred.connect(self.on_error_occurred)
        
        # 按钮连接
        self.start_button.clicked.connect(self.start_processing)
        self.stop_button.clicked.connect(self.stop_processing)
    
    def load_default_params(self):
        """加载默认参数"""
        try:
            # 先尝试加载默认模板
            default_template = self.template_manager.get_default_template()
            if default_template:
                params = self.template_manager.load_template(default_template)
                if params:
                    self.current_params = params
                    self.logger.info(f"已加载默认模板: {default_template}")
                    return
            
            # 如果没有默认模板,使用出厂默认值
            self.current_params = PrimerParams()
            self.logger.info("已加载出厂默认参数")
        except Exception as e:
            self.logger.error(f"加载默认参数失败: {e}")
    
    def get_current_params(self) -> Optional[PrimerParams]:
        """获取当前参数设置"""
        return self.current_params
    
    # ========== 槽函数 ==========
    
    @pyqtSlot()
    def start_processing(self):
        """开始处理（增强版）"""
        try:
            # 检查输入
            input_text = self.input_text.toPlainText().strip()
            if not input_text:
                CustomMessageBox.show_warning(
                    self,
                    "输入为空",
                    "请先输入染色体坐标信息"
                )
                return
            
            # 检查任务状态
            if not self.controller.can_start_new_task():
                CustomMessageBox.show_warning(
                    self,
                    "任务冲突",
                    f"当前任务状态为 {self.controller.task_state.value}，\n"
                    f"请等待当前任务完成后再开始新任务。"
                )
                return
            
            # 获取参数
            params = self.get_current_params()
            if not params:
                return
            
            # 检查是否有前一个线程还在运行
            if self.worker_thread and self.worker_thread.isRunning():
                self.logger.warning("前一个工作线程仍在运行，等待其结束")
                self.worker_thread.quit()
                self.worker_thread.wait(2000)  # 等待最多2秒
            
            # 在后台线程中处理
            self.worker_thread = WorkerThread(
                self.controller,
                input_text,
                self.version_combo.currentText(),
                self.browser_combo.currentText(),
                params
            )
            self.worker_thread.start()
            
        except Exception as e:
            self.logger.error(f"启动任务时出错: {e}", exc_info=True)
            CustomMessageBox.show_error(
                self,
                "启动失败",
                f"启动任务时发生错误:\n{str(e)}"
            )
    
    @pyqtSlot()
    def stop_processing(self):
        """停止处理（增强版）"""
        try:
            # 确认停止
            if self.controller.task_state.value in ['running', 'initializing']:
                reply = CustomMessageBox.show_question(
                    self,
                    "确认停止",
                    "确定要停止当前任务吗？\n当前正在处理的坐标会完成后停止。"
                )
                if reply != QMessageBox.Yes:
                    return
            
            # 请求停止
            self.controller.stop_processing()
            self._add_progress_message("正在停止任务，请稍候...", "⏹")
            
            # 禁用停止按钮，防止重复点击
            self.stop_button.setEnabled(False)
            
        except Exception as e:
            self.logger.error(f"停止处理时出错: {e}", exc_info=True)
            CustomMessageBox.show_error(
                self,
                "停止失败",
                f"停止任务时发生错误:\n{str(e)}"
            )
    
    @pyqtSlot(str)
    def on_progress_updated(self, message: str):
        """进度更新 - 从信号触发"""
        self._add_progress_message(message, "➡️")
    
    def _add_progress_message(self, message: str, icon: str = "➡️"):
        """添加进度消息到显示区域"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.progress_display.appendPlainText(f"{icon} [{timestamp}] {message}")
        self.progress_display.ensureCursorVisible()
    
    @pyqtSlot(ProcessingStats)
    def on_stats_updated(self, stats: ProcessingStats):
        """统计更新"""
        self.progress_bar.setMaximum(stats.total)
        self.progress_bar.setValue(stats.processed)
        
        self.stats_label.setText(
            f"总计: {stats.total} | "
            f"成功: <font color='#16a34a'>{stats.success}</font> | "
            f"失败: <font color='#dc2626'>{stats.failed}</font>"
        )
    
    @pyqtSlot()
    def on_task_started(self):
        """任务开始"""
        try:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setValue(0)
            self.progress_display.clear()
            self._add_progress_message("任务已启动", "🚀")
        except Exception as e:
            self.logger.error(f"任务启动UI更新失败: {e}", exc_info=True)
    
    @pyqtSlot(ProcessingStats)
    def on_task_completed(self, stats: ProcessingStats):
        """任务完成"""
        try:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # 显示详细完成信息
            success_rate = (stats.success / stats.total * 100) if stats.total > 0 else 0
            CustomMessageBox.show_success(
                self,
                "任务完成",
                f"处理完成!\n\n"
                f"总计: {stats.total} 组\n"
                f"成功: {stats.success} 组\n"
                f"失败: {stats.failed} 组\n"
                f"成功率: {success_rate:.1f}%"
            )
            self._add_progress_message(
                f"任务完成 - 成功率 {success_rate:.1f}%", 
                "✅"
            )
        except Exception as e:
            self.logger.error(f"任务完成UI更新失败: {e}", exc_info=True)
    
    @pyqtSlot()
    def on_task_stopped(self):
        """任务停止"""
        try:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            CustomMessageBox.show_info(
                self,
                "任务已停止",
                "任务已被用户停止"
            )
            self._add_progress_message("任务已停止", "⏹")
        except Exception as e:
            self.logger.error(f"任务停止UI更新失败: {e}", exc_info=True)
    
    @pyqtSlot(str, str)
    def on_error_occurred(self, title: str, message: str):
        """错误发生（增强版）"""
        try:
            # 恢复UI状态
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # 显示错误信息
            CustomMessageBox.show_error(self, title, message)
            self._add_progress_message(f"错误: {title} - {message}", "❌")
            
            # 检查是否是浏览器相关错误
            if "浏览器" in message or "driver" in message.lower():
                self._add_progress_message(
                    "提示: 可尝试更新浏览器驱动（工具 → 更新浏览器驱动）", 
                    "💡"
                )
        except Exception as e:
            self.logger.error(f"错误处理UI更新失败: {e}", exc_info=True)
    

    
    # ========== 菜单操作 ==========
    
    def import_coordinates(self):
        """导入坐标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择坐标文件",
            "",
            "文本文件 (*.txt *.csv);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.setPlainText(content)
                self._add_progress_message(f"已从文件导入坐标: {os.path.basename(file_path)}", "📥")
            except Exception as e:
                CustomMessageBox.show_error(self, "导入失败", str(e))
    
    def export_coordinates(self):
        """导出坐标"""
        content = self.input_text.toPlainText()
        if not content.strip():
            CustomMessageBox.show_warning(self, "无数据", "没有可导出的坐标数据")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存坐标文件",
            "coordinates.txt",
            "文本文件 (*.txt);;CSV文件 (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._add_progress_message(f"坐标已导出至: {os.path.basename(file_path)}", "📤")
            except Exception as e:
                CustomMessageBox.show_error(self, "导出失败", str(e))
    
    def clear_input(self):
        """清空输入"""
        reply = CustomMessageBox.show_question(
            self,
            "确认清空",
            "确定要清空所有输入和日志吗？"
        )
        if reply == QMessageBox.Yes:
            self.input_text.clear()
            self.progress_display.clear()
            self.stats_label.setText("就绪")
            self.progress_bar.setValue(0)
    
    def validate_coordinates(self):
        """验证坐标"""
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            CustomMessageBox.show_warning(self, "输入为空", "请先输入坐标")
            return
        
        valid, invalid = self.controller.validate_input(
            input_text,
            self.version_combo.currentText()
        )
        
        msg = f"有效: {len(valid)} 组\n无效: {len(invalid)} 组"
        
        if invalid:
            details = "\n".join([
                f"第{r.line_number}行: {r.error_message}"
                for r in invalid[:10]
            ])
            CustomMessageBox.show_info(self, "验证结果", msg, details)
            self._add_progress_message(f"坐标验证完成。有效: {len(valid)}, 无效: {len(invalid)}", "⚠️")
        else:
            CustomMessageBox.show_success(self, "验证通过", msg)
            self._add_progress_message(f"坐标验证通过，共 {len(valid)} 组有效。", "✅")
    

    
    def manage_templates(self):
        """管理模板"""
        try:
            dialog = TemplateDialog(self.template_manager, self)
            if dialog.exec_() == QDialog.Accepted:
                # 如果用户在对话框中选择了模板,加载它
                selected_template = dialog.get_selected_template()
                if selected_template:
                    params = self.template_manager.load_template(selected_template)
                    if params:
                        self.set_params(params)
                        self._add_progress_message(f"已加载模板: {selected_template}", "📋")
        except Exception as e:
            self.logger.error(f"打开模板管理对话框失败: {e}", exc_info=True)
            CustomMessageBox.show_error(
                self,
                "错误",
                f"无法打开模板管理对话框:\n{str(e)}"
            )
    
    def update_driver(self):
        """更新驱动"""
        try:
            dialog = DriverUpdateDialog(self)
            dialog.exec_()
        except Exception as e:
            self.logger.error(f"打开驱动更新对话框失败: {e}", exc_info=True)
            CustomMessageBox.show_error(
                self,
                "错误",
                f"无法打开驱动更新对话框:\n{str(e)}"
            )
    
    def download_chain_file(self):
        """下载坐标转换文件"""
        try:
            # 获取目标目录
            target_dir = get_resource_path("resources/hg19ToHg38")
            
            dialog = ChainFileDownloadDialog(target_dir, self)
            dialog.exec_()
        except Exception as e:
            self.logger.error(f"打开坐标转换文件下载对话框失败: {e}", exc_info=True)
            CustomMessageBox.show_error(
                self,
                "错误",
                f"无法打开下载对话框:\n{str(e)}"
            )
    
    def validate_page_elements(self):
        """验证网页元素"""
        try:
            # 先检查浏览器是否已启动
            if not self.controller.web_service.driver:
                CustomMessageBox.show_info(
                    self,
                    "提示",
                    "请先启动一次浏览器(开始设计引物)后再进行验证"
                )
                return
            
            # 确保在正确的页面
            current_url = self.controller.web_service.driver.current_url
            if "primer-blast" not in current_url.lower():
                reply = CustomMessageBox.show_question(
                    self,
                    "需要打开页面",
                    "当前不在Primer-BLAST页面,是否自动打开?"
                )
                if reply == QMessageBox.Yes:
                    self.controller.web_service.open_primer_blast()
                else:
                    return
            
            # 执行验证
            self._add_progress_message("正在验证页面元素...", "🔍")
            success = self.controller.web_service.page.validate_page_elements()
            
            if success:
                CustomMessageBox.show_success(
                    self,
                    "验证通过",
                    "所有关键页面元素都能正常定位,网站未发生重大变更"
                )
            else:
                CustomMessageBox.show_warning(
                    self,
                    "验证失败",
                    "部分关键元素无法定位,网站可能已更新。\n"
                    "程序会尝试使用备用定位策略,但建议检查日志了解详情。"
                )
        except Exception as e:
            self.logger.error(f"页面验证失败: {e}", exc_info=True)
            CustomMessageBox.show_error(
                self,
                "验证出错",
                f"页面验证过程中发生错误:\n{str(e)}"
            )
    
    def close_browser(self):
        """关闭浏览器（增强版）"""
        try:
            # 检查是否有任务正在运行
            if self.controller.is_running:
                reply = CustomMessageBox.show_question(
                    self,
                    "确认关闭",
                    "任务正在运行中，关闭浏览器将终止当前任务。\n\n"
                    "确定要关闭浏览器吗？"
                )
                if reply != QMessageBox.Yes:
                    return
                
                # 先停止任务
                self.controller.stop_processing()
            
            # 关闭浏览器
            self.controller.close_browser()
            self._add_progress_message("浏览器已关闭", "🌐")
            
            CustomMessageBox.show_info(
                self,
                "浏览器已关闭",
                "浏览器已成功关闭。\n\n"
                "下次开始任务时将自动重新启动浏览器。"
            )
            
        except Exception as e:
            self.logger.error(f"关闭浏览器时出错: {e}", exc_info=True)
            CustomMessageBox.show_error(
                self,
                "关闭失败",
                f"关闭浏览器时发生错误:\n{str(e)}"
            )
    
    def show_usage(self):
        """显示使用说明"""
        usage_text = """
        <h2>引物设计工具使用说明</h2>
        
        <h3>1. 输入坐标</h3>
        <p>在"批量基因组坐标输入"区域输入染色体坐标，每行一组。<br>
        格式：<code>chr1 123456</code> 或 <code>1 123456</code></p>
        
        <h3>2. 选择参数</h3>
        <p>在"引物参数设置"区域配置引物设计参数。<br>
        可以保存常用参数为模板，方便下次使用。</p>
        
        <h3>3. 开始设计</h3>
        <p>点击"开始设计引物"按钮，程序会自动：<br>
        • 验证坐标有效性<br>
        • 转换hg19坐标到hg38（如需要）<br>
        • 启动浏览器<br>
        • 自动填写Primer-BLAST表单<br>
        • 提交设计任务</p>
        
        <h3>4. 查看结果</h3>
        <p>结果会在新的浏览器标签页中打开。</p>
        """
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("使用说明")
        msg.setTextFormat(Qt.RichText)
        msg.setText(usage_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_about(self):
        """显示关于"""
        about_text = f"""
        <h2>{self.config.APP_NAME}</h2>
        <p><b>版本:</b> {self.config.APP_VERSION}</p>
        <p><b>功能:</b> NCBI Primer-BLAST 自动化工具</p>
        <br>
        <p>本工具可以批量处理染色体坐标，自动提交引物设计任务到 NCBI Primer-BLAST。</p>
        <br>
        <p><b>主要特性:</b></p>
        <ul>
        <li>批量处理多组坐标</li>
        <li>自动坐标转换（hg19 → hg38）</li>
        <li>参数模板管理</li>
        <li>任务进度跟踪</li>
        <li>错误重试机制</li>
        </ul>
        """
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("关于")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def closeEvent(self, event):
        """关闭事件（增强版）- 确保资源安全清理"""
        try:
            # 检查是否有任务正在运行
            if self.controller.is_running:
                reply = CustomMessageBox.show_question(
                    self,
                    "确认退出",
                    "任务正在运行中，确定要退出吗？\n\n"
                    "退出将停止当前任务并关闭浏览器。"
                )
                if reply != QMessageBox.Yes:
                    event.ignore()
                    return
                
                # 停止任务
                self.controller.stop_processing()
                
                # 等待任务停止（最多等待3秒）
                if self.worker_thread and self.worker_thread.isRunning():
                    self.worker_thread.quit()
                    self.worker_thread.wait(3000)  # 等待最多3秒
            
            # 关闭浏览器
            try:
                self.controller.close_browser()
            except Exception as e:
                self.logger.warning(f"关闭浏览器时出错: {e}")
            
            # 接受关闭事件
            event.accept()
            self.logger.info("程序正常退出")
            
        except Exception as e:
            self.logger.error(f"关闭程序时出错: {e}", exc_info=True)
            # 即使出错也允许关闭
            event.accept()
