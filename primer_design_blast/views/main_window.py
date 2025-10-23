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
from PyQt5.QtGui import QIcon, QColor, QTextCursor
from PyQt5.QtGui import QIcon, QFont, QColor

from ..models.primer_params import PrimerParams
from ..models.config import AppConfig, TemplateManager
from ..controllers.primer_controller import PrimerController, ProcessingStats
from ..utils.resource_utils import get_resource_path
from .components.message_box import CustomMessageBox
from .components.template_dialog import TemplateDialog
from .components.driver_update_dialog import DriverUpdateDialog
from .components.collapsible_box import CollapsibleBox


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
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 设置中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建各个区域
        main_layout.addWidget(self.create_input_area())
        main_layout.addWidget(self.create_parameter_area())
        main_layout.addWidget(self.create_progress_area())
        main_layout.addLayout(self.create_control_buttons())
        
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
        save_template_action.triggered.connect(self.save_template)
        template_menu.addAction(save_template_action)

        load_template_action = QAction("加载参数模板...", self)
        load_template_action.triggered.connect(self.load_template)
        template_menu.addAction(load_template_action)

        manage_template_action = QAction("管理模板...", self)
        manage_template_action.triggered.connect(self.manage_templates)
        template_menu.addAction(manage_template_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        driver_update_action = QAction("更新浏览器驱动...", self)
        driver_update_action.triggered.connect(self.update_driver)
        tools_menu.addAction(driver_update_action)

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
        group = QGroupBox("批量基因组坐标输入")
        self.add_shadow(group)

        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(12)

        # 多行输入
        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText(
            "请输入染色体坐标信息，每行一组\n\n"
            "格式示例：\n"
            "chr1 123456  (染色体号 + 空格 + 位点)\n"
            "chr2 234567\n"
            "X 345678\n\n"
            "支持 1-22 号染色体及 X、Y 染色体\n"
            "提示：可以粘贴多行数据，程序会自动批量处理"
        )
        self.input_text.setMaximumHeight(150)
        self.input_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        layout.addRow("坐标内容:", self.input_text)
        
        # 基因组版本
        self.version_combo = QComboBox()
        self.version_combo.addItems(["hg38/GRCh38", "hg19/GRCh37"])
        self.version_combo.setMinimumWidth(160)
        layout.addRow("基因组版本:", self.version_combo)

        # 浏览器选择
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Edge", "Chrome"])
        self.browser_combo.setMinimumWidth(160)
        layout.addRow("浏览器:", self.browser_combo)
        
        group.setLayout(layout)
        return group
    
    def create_parameter_area(self) -> CollapsibleBox:
        """创建参数设置区域"""
        # 创建可折叠组件
        self.param_collapsible = CollapsibleBox("引物参数设置")
        
        # 创建参数内容容器
        param_content = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # PCR产物大小
        pcr_layout = QHBoxLayout()
        pcr_layout.addWidget(QLabel("PCR产物大小 (bp):"))
        self.pcr_min_input = QLineEdit("100")
        self.pcr_min_input.setMaximumWidth(80)
        pcr_layout.addWidget(self.pcr_min_input)
        pcr_layout.addWidget(QLabel(" - "))
        self.pcr_max_input = QLineEdit("1200")
        self.pcr_max_input.setMaximumWidth(80)
        pcr_layout.addWidget(self.pcr_max_input)
        pcr_layout.addStretch()
        layout.addLayout(pcr_layout)
        
        # Tm值
        tm_layout = QHBoxLayout()
        tm_layout.addWidget(QLabel("Tm值 (°C):"))
        self.tm_min_input = QLineEdit("58")
        self.tm_min_input.setPlaceholderText("最小")
        self.tm_min_input.setMaximumWidth(60)
        tm_layout.addWidget(self.tm_min_input)
        
        self.tm_opt_input = QLineEdit("60")
        self.tm_opt_input.setPlaceholderText("最佳")
        self.tm_opt_input.setMaximumWidth(60)
        tm_layout.addWidget(self.tm_opt_input)
        
        self.tm_max_input = QLineEdit("62")
        self.tm_max_input.setPlaceholderText("最大")
        self.tm_max_input.setMaximumWidth(60)
        tm_layout.addWidget(self.tm_max_input)
        
        tm_layout.addWidget(QLabel("   最大差值:"))
        self.tm_diff_input = QLineEdit("2")
        self.tm_diff_input.setMaximumWidth(60)
        tm_layout.addWidget(self.tm_diff_input)
        tm_layout.addStretch()
        layout.addLayout(tm_layout)
        
        # 引物大小
        primer_layout = QHBoxLayout()
        primer_layout.addWidget(QLabel("引物大小 (bp):"))
        self.primer_min_input = QLineEdit("18")
        self.primer_min_input.setPlaceholderText("最小")
        self.primer_min_input.setMaximumWidth(60)
        primer_layout.addWidget(self.primer_min_input)
        
        self.primer_opt_input = QLineEdit("20")
        self.primer_opt_input.setPlaceholderText("最佳")
        self.primer_opt_input.setMaximumWidth(60)
        primer_layout.addWidget(self.primer_opt_input)
        
        self.primer_max_input = QLineEdit("25")
        self.primer_max_input.setPlaceholderText("最大")
        self.primer_max_input.setMaximumWidth(60)
        primer_layout.addWidget(self.primer_max_input)
        primer_layout.addStretch()
        layout.addLayout(primer_layout)
        
        # 其他参数
        other_layout = QFormLayout()
        other_layout.setHorizontalSpacing(14)
        other_layout.setVerticalSpacing(10)
        self.primer_num_input = QLineEdit("10")
        self.primer_num_input.setMaximumWidth(100)
        other_layout.addRow("返回引物数:", self.primer_num_input)
        
        self.gc_max_input = QLineEdit("4")
        self.gc_max_input.setMaximumWidth(100)
        other_layout.addRow("3'端最大GC:", self.gc_max_input)
        
        self.poly_max_input = QLineEdit("4")
        self.poly_max_input.setMaximumWidth(100)
        other_layout.addRow("最大连续碱基:", self.poly_max_input)
        
        self.ext_left_input = QLineEdit("800")
        self.ext_left_input.setMaximumWidth(100)
        other_layout.addRow("左侧扩展 (bp):", self.ext_left_input)
        
        self.ext_right_input = QLineEdit("800")
        self.ext_right_input.setMaximumWidth(100)
        other_layout.addRow("右侧扩展 (bp):", self.ext_right_input)
        
        layout.addLayout(other_layout)
        
        # 参数管理按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        reset_btn = QPushButton("🔄 重置为默认")
        reset_btn.setMaximumWidth(120)
        reset_btn.clicked.connect(self.reset_to_default_params)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                color: #4f5d6d;
                font-size: 11px;
                border-radius: 4px;
                padding: 4px 8px;
                border: 1px solid #d0d7de;
            }
            QPushButton:hover {
                background-color: #e7eaef;
            }
        """)
        
        save_btn = QPushButton("💾 保存模板")
        save_btn.setMaximumWidth(120)
        save_btn.clicked.connect(self.save_template)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                color: #4f5d6d;
                font-size: 11px;
                border-radius: 4px;
                padding: 4px 8px;
                border: 1px solid #d0d7de;
            }
            QPushButton:hover {
                background-color: #e7eaef;
            }
        """)
        
        load_btn = QPushButton("📂 加载模板")
        load_btn.setMaximumWidth(120)
        load_btn.clicked.connect(self.load_template)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                color: #4f5d6d;
                font-size: 11px;
                border-radius: 4px;
                padding: 4px 8px;
                border: 1px solid #d0d7de;
            }
            QPushButton:hover {
                background-color: #e7eaef;
            }
        """)
        
        manage_btn = QPushButton("⚙️ 管理模板")
        manage_btn.setMaximumWidth(120)
        manage_btn.clicked.connect(self.manage_templates)
        manage_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                color: #4f5d6d;
                font-size: 11px;
                border-radius: 4px;
                padding: 4px 8px;
                border: 1px solid #d0d7de;
            }
            QPushButton:hover {
                background-color: #e7eaef;
            }
        """)
        
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(load_btn)
        button_layout.addWidget(manage_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 设置布局到参数内容容器
        param_content.setLayout(layout)
        
        # 将内容添加到可折叠组件
        self.param_collapsible.add_widget(param_content)
        
        # 连接折叠状态改变信号
        self.param_collapsible.collapsed_changed.connect(self.on_param_collapsed_changed)
        
        return self.param_collapsible
    
    def create_progress_area(self) -> QGroupBox:
        """创建进度显示区域"""
        group = QGroupBox("运行进度")
        self.add_shadow(group)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p% (%v/%m)")
        layout.addWidget(self.progress_bar)
        
        # 统计信息标签
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("就绪")
        self.stats_label.setStyleSheet("color: #4b5563; font-weight: 600;")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 日志显示
        self.progress_display = QPlainTextEdit()
        self.progress_display.setReadOnly(True)
        self.progress_display.setMaximumHeight(200)
        self.progress_display.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: #f6f7f9;
                color: #1f2937;
                border: 1px solid #cfd5de;
            }
        """)
        self.progress_display.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.progress_display.setMaximumBlockCount(500)
        layout.addWidget(self.progress_display)
        
        group.setLayout(layout)
        return group
    
    def create_control_buttons(self) -> QHBoxLayout:
        """创建控制按钮"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # 开始按钮
        self.start_button = QPushButton("开始设计引物")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2f6fed;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
                padding: 6px 18px;
                border: 1px solid #2559c2;
            }
            QPushButton:hover {
                background-color: #2559c2;
                border: 1px solid #1f4aa3;
            }
            QPushButton:pressed {
                background-color: #1f4aa3;
            }
            QPushButton:disabled {
                background-color: #d6dce5;
                color: #8b95a3;
                border: 1px solid #c7ced8;
            }
        """)
        self.start_button.clicked.connect(self.start_processing)
        
        # 停止按钮
        self.stop_button = QPushButton("停止处理")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #c53f32;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
                padding: 6px 18px;
                border: 1px solid #a4362b;
            }
            QPushButton:hover {
                background-color: #a4362b;
                border: 1px solid #8c2f26;
            }
            QPushButton:pressed {
                background-color: #8c2f26;
            }
            QPushButton:disabled {
                background-color: #d6dce5;
                color: #8b95a3;
                border: 1px solid #c7ced8;
            }
        """)
        self.stop_button.clicked.connect(self.stop_processing)
        
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        
        return layout
    
    def add_shadow(self, widget):
        """添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(32, 45, 64, 40))
        widget.setGraphicsEffect(shadow)
    
    def apply_styles(self):
        """应用全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f5f7;
            }
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                color: #1f2933;
            }
            QMenuBar {
                background-color: #f8f9fb;
                border-bottom: 1px solid #d1d7e0;
            }
            QMenuBar::item {
                spacing: 6px;
                padding: 4px 12px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #e4e8ef;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d1d7e0;
            }
            QMenu::item:selected {
                background-color: #e4e8ef;
            }
            QGroupBox {
                font-size: 13px;
                font-weight: 600;
                border: 1px solid #d1d7e0;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 18px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 6px;
                color: #4b5563;
            }
            QLabel {
                font-size: 12px;
                color: #3f4c5d;
            }
            QLineEdit, QComboBox, QPlainTextEdit {
                border: 1px solid #c3cad4;
                border-radius: 6px;
                padding: 6px;
                background-color: #f9fafb;
                color: #1f2933;
                selection-background-color: #b9cdf0;
                selection-color: #0f172a;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #c3cad4;
                selection-background-color: #e4e8ef;
            }
            QLineEdit:focus, QPlainTextEdit:focus {
                border: 1px solid #365f9c;
            }
            QProgressBar {
                background-color: #edf0f4;
                border: 1px solid #d1d7e0;
                border-radius: 6px;
                color: #1f2933;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #365f9c;
                border-radius: 6px;
            }
            QScrollBar:vertical {
                background: #e6e9ee;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c4cad3;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #aab2be;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def setup_connections(self):
        """设置信号连接"""
        self.controller.progress_updated.connect(self.on_progress_updated)
        self.controller.stats_updated.connect(self.on_stats_updated)
        self.controller.task_started.connect(self.on_task_started)
        self.controller.task_completed.connect(self.on_task_completed)
        self.controller.task_stopped.connect(self.on_task_stopped)
        self.controller.error_occurred.connect(self.on_error_occurred)
    
    def load_default_params(self):
        """加载默认参数"""
        try:
            # 先尝试加载默认模板
            default_template = self.template_manager.get_default_template()
            if default_template:
                params = self.template_manager.load_template(default_template)
                if params:
                    self.set_params(params)
                    self.logger.info(f"已加载默认模板: {default_template}")
                    self.on_progress_updated(f"已自动加载默认模板: {default_template}", "⭐")
                    return
            
            # 如果没有默认模板,使用出厂默认值
            params = PrimerParams()
            self.set_params(params)
            self.logger.info("已加载出厂默认参数")
        except Exception as e:
            self.logger.error(f"加载默认参数失败: {e}")
    
    def get_current_params(self) -> Optional[PrimerParams]:
        """获取当前参数设置"""
        try:
            params = PrimerParams(
                pcr_min=int(self.pcr_min_input.text()),
                pcr_max=int(self.pcr_max_input.text()),
                tm_min=float(self.tm_min_input.text()),
                tm_opt=float(self.tm_opt_input.text()),
                tm_max=float(self.tm_max_input.text()),
                tm_max_difference=int(self.tm_diff_input.text()),
                primer_min_size=int(self.primer_min_input.text()),
                primer_opt_size=int(self.primer_opt_input.text()),
                primer_max_size=int(self.primer_max_input.text()),
                primer_num_return=int(self.primer_num_input.text()),
                end_gc_max=int(self.gc_max_input.text()),
                max_poly_x=int(self.poly_max_input.text()),
                extension_left=int(self.ext_left_input.text()),
                extension_right=int(self.ext_right_input.text())
            )
            return params
        except ValueError as e:
            CustomMessageBox.show_error(
                self,
                "参数错误",
                f"参数格式不正确：{str(e)}"
            )
            return None
    
    def set_params(self, params: PrimerParams):
        """设置参数到界面"""
        self.pcr_min_input.setText(str(params.pcr_min))
        self.pcr_max_input.setText(str(params.pcr_max))
        self.tm_min_input.setText(str(params.tm_min))
        self.tm_opt_input.setText(str(params.tm_opt))
        self.tm_max_input.setText(str(params.tm_max))
        self.tm_diff_input.setText(str(params.tm_max_difference))
        self.primer_min_input.setText(str(params.primer_min_size))
        self.primer_opt_input.setText(str(params.primer_opt_size))
        self.primer_max_input.setText(str(params.primer_max_size))
        self.primer_num_input.setText(str(params.primer_num_return))
        self.gc_max_input.setText(str(params.end_gc_max))
        self.poly_max_input.setText(str(params.max_poly_x))
        self.ext_left_input.setText(str(params.extension_left))
        self.ext_right_input.setText(str(params.extension_right))
    
    # ========== 槽函数 ==========
    
    @pyqtSlot()
    def start_processing(self):
        """开始处理"""
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            CustomMessageBox.show_warning(
                self,
                "输入为空",
                "请先输入染色体坐标信息"
            )
            return
        
        params = self.get_current_params()
        if not params:
            return
        
        # 在后台线程中处理
        self.worker_thread = WorkerThread(
            self.controller,
            input_text,
            self.version_combo.currentText(),
            self.browser_combo.currentText(),
            params
        )
        self.worker_thread.start()
    
    @pyqtSlot()
    def stop_processing(self):
        """停止处理"""
        self.controller.stop_processing()
    
    @pyqtSlot(str)
    def on_progress_updated(self, message: str):
        """进度更新"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.progress_display.appendPlainText(f"[{timestamp}] {message}")
        cursor = self.progress_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.progress_display.setTextCursor(cursor)
        self.progress_display.ensureCursorVisible()
    
    @pyqtSlot(ProcessingStats)
    def on_stats_updated(self, stats: ProcessingStats):
        """统计更新"""
        self.progress_bar.setMaximum(stats.total)
        self.progress_bar.setValue(stats.processed)
        
        self.stats_label.setText(
            f"总计: {stats.total} | "
            f"已处理: {stats.processed} | "
            f"成功: {stats.success} | "
            f"失败: {stats.failed}"
        )
    
    @pyqtSlot()
    def on_task_started(self):
        """任务开始"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
    
    @pyqtSlot(ProcessingStats)
    def on_task_completed(self, stats: ProcessingStats):
        """任务完成"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        CustomMessageBox.show_success(
            self,
            "任务完成",
            f"成功处理 {stats.success}/{stats.total} 组数据"
        )
    
    @pyqtSlot()
    def on_task_stopped(self):
        """任务停止"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    @pyqtSlot(str, str)
    def on_error_occurred(self, title: str, message: str):
        """错误发生"""
        CustomMessageBox.show_error(self, title, message)
    
    def on_param_collapsed_changed(self, is_collapsed: bool):
        """参数区域折叠状态改变"""
        # 使用QTimer延迟调整,确保动画完成
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(self.param_collapsible.animation_duration + 50, self.adjust_window_size)
    
    def adjust_window_size(self):
        """根据内容调整窗口大小"""
        try:
            # 获取当前窗口大小
            current_size = self.size()
            
            # 计算理想高度
            ideal_height = self.centralWidget().sizeHint().height() + self.menuBar().height() + 50
            
            # 限制在合理范围内
            min_height = 600
            max_height = 900
            new_height = max(min_height, min(ideal_height, max_height))
            
            # 平滑调整窗口大小
            if abs(new_height - current_size.height()) > 50:  # 只在变化较大时调整
                self.resize(current_size.width(), new_height)
        except Exception as e:
            self.logger.debug(f"调整窗口大小时出错: {e}")
    
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
                self.on_progress_updated(f"已导入: {file_path}")
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
            "",
            "文本文件 (*.txt);;CSV文件 (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.on_progress_updated(f"已导出: {file_path}")
            except Exception as e:
                CustomMessageBox.show_error(self, "导出失败", str(e))
    
    def clear_input(self):
        """清空输入"""
        reply = CustomMessageBox.show_question(
            self,
            "确认清空",
            "确定要清空所有输入吗？"
        )
        if reply == QMessageBox.Yes:
            self.input_text.clear()
            self.progress_display.clear()
    
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
        else:
            CustomMessageBox.show_success(self, "验证通过", msg)
    
    def save_template(self):
        """保存模板"""
        params = self.get_current_params()
        if not params:
            return
        
        name, ok = QInputDialog.getText(self, "保存模板", "模板名称:")
        if ok and name:
            if self.template_manager.save_template(name, params):
                CustomMessageBox.show_success(
                    self,
                    "保存成功",
                    f"模板 '{name}' 已保存"
                )
            else:
                CustomMessageBox.show_error(self, "保存失败", "无法保存模板")
    
    def load_template(self):
        """加载模板"""
        names = self.template_manager.get_template_names()
        if not names:
            CustomMessageBox.show_info(self, "无模板", "还没有保存的模板")
            return
        
        name, ok = QInputDialog.getItem(
            self,
            "加载模板",
            "选择模板:",
            names,
            0,
            False
        )
        
        if ok and name:
            params = self.template_manager.load_template(name)
            if params:
                self.set_params(params)
                self.on_progress_updated(f"已加载模板: {name}")
            else:
                CustomMessageBox.show_error(self, "加载失败", "无法加载模板")
    
    def reset_to_default_params(self):
        """重置为默认参数"""
        reply = CustomMessageBox.show_question(
            self,
            "确认重置",
            "确定要将参数重置为默认值吗？"
        )
        if reply == QMessageBox.Yes:
            default_params = PrimerParams()  # 获取默认参数
            self.set_params(default_params)
            self.on_progress_updated("已重置为默认参数", "🔄")
            CustomMessageBox.show_success(self, "重置成功", "参数已重置为默认值")
    
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
                        self.on_progress_updated(f"已加载模板: {selected_template}", "📋")
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
            self.on_progress_updated("正在验证页面元素...", "🔍")
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
        """关闭浏览器"""
        self.controller.close_browser()
    
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
        """关闭事件"""
        if self.controller.is_running:
            reply = CustomMessageBox.show_question(
                self,
                "确认退出",
                "任务正在运行，确定要退出吗？"
            )
            if reply == QMessageBox.Yes:
                self.controller.stop_processing()
                self.controller.close_browser()
                event.accept()
            else:
                event.ignore()
        else:
            self.controller.close_browser()
            event.accept()
