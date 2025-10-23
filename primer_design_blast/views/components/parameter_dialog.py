# -*- coding: utf-8 -*-
"""
引物参数设置对话框
独立的参数设置窗口
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QGroupBox, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from ...models.primer_params import PrimerParams
from ...models.config import TemplateManager
from ...utils.resource_utils import get_resource_path
from .message_box import CustomMessageBox


class ParameterDialog(QDialog):
    """引物参数设置对话框"""
    
    def __init__(self, current_params: PrimerParams = None, parent=None):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self.current_params = current_params or PrimerParams()
        
        self.init_ui()
        self.set_params(self.current_params)
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("引物参数设置")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        # 设置图标
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 参数表单
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(25)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # PCR产物大小
        self.pcr_min_input = QLineEdit()
        self.pcr_max_input = QLineEdit()
        pcr_layout = self._create_min_max_layout(self.pcr_min_input, self.pcr_max_input)
        form_layout.addRow("PCR产物大小 (bp):", pcr_layout)
        
        # Tm值
        self.tm_min_input = QLineEdit()
        self.tm_opt_input = QLineEdit()
        self.tm_max_input = QLineEdit()
        self.tm_diff_input = QLineEdit()
        tm_layout = self._create_tm_layout(
            self.tm_min_input, self.tm_opt_input, self.tm_max_input, self.tm_diff_input
        )
        form_layout.addRow("Tm值 (°C):", tm_layout)
        
        # 引物大小
        self.primer_min_input = QLineEdit()
        self.primer_opt_input = QLineEdit()
        self.primer_max_input = QLineEdit()
        primer_size_layout = self._create_min_opt_max_layout(
            self.primer_min_input, self.primer_opt_input, self.primer_max_input
        )
        form_layout.addRow("引物大小 (bp):", primer_size_layout)
        
        # 返回引物数
        self.primer_num_input = QLineEdit()
        form_layout.addRow("返回引物数:", self.primer_num_input)
        
        # 3'端最大GC
        self.gc_max_input = QLineEdit()
        form_layout.addRow("3'端最大GC:", self.gc_max_input)
        
        # 最大连续碱基
        self.poly_max_input = QLineEdit()
        form_layout.addRow("最大连续碱基:", self.poly_max_input)
        
        # 左右扩展
        self.ext_left_input = QLineEdit()
        self.ext_right_input = QLineEdit()
        ext_layout = self._create_min_max_layout(self.ext_left_input, self.ext_right_input, "左", "右")
        form_layout.addRow("序列扩展 (bp):", ext_layout)
        
        layout.addLayout(form_layout)
        
        # 模板管理按钮
        template_layout = QHBoxLayout()
        template_layout.setSpacing(10)
        
        reset_btn = QPushButton("重置为默认")
        reset_btn.clicked.connect(self.reset_to_default)
        
        load_btn = QPushButton("加载模板")
        load_btn.clicked.connect(self.load_template)
        
        save_btn = QPushButton("保存为模板")
        save_btn.clicked.connect(self.save_template)
        
        template_layout.addWidget(reset_btn)
        template_layout.addWidget(load_btn)
        template_layout.addWidget(save_btn)
        template_layout.addStretch()
        
        layout.addLayout(template_layout)
        
        # 确定/取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.apply_styles()
    
    def _create_min_max_layout(self, min_widget, max_widget, min_label="最小", max_label="最大"):
        """创建最小-最大值输入布局"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel(f"{min_label}:"))
        min_widget.setFixedWidth(90)
        layout.addWidget(min_widget)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel(f"{max_label}:"))
        max_widget.setFixedWidth(90)
        layout.addWidget(max_widget)
        
        layout.addStretch()
        return layout
    
    def _create_min_opt_max_layout(self, min_widget, opt_widget, max_widget):
        """创建最小-最优-最大值输入布局"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("最小:"))
        min_widget.setFixedWidth(70)
        layout.addWidget(min_widget)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("最优:"))
        opt_widget.setFixedWidth(70)
        layout.addWidget(opt_widget)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("最大:"))
        max_widget.setFixedWidth(70)
        layout.addWidget(max_widget)
        
        layout.addStretch()
        return layout
    
    def _create_tm_layout(self, min_widget, opt_widget, max_widget, diff_widget):
        """创建Tm值输入布局"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("最小:"))
        min_widget.setFixedWidth(60)
        layout.addWidget(min_widget)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("最优:"))
        opt_widget.setFixedWidth(60)
        layout.addWidget(opt_widget)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("最大:"))
        max_widget.setFixedWidth(60)
        layout.addWidget(max_widget)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("最大差值:"))
        diff_widget.setFixedWidth(60)
        layout.addWidget(diff_widget)
        
        layout.addStretch()
        return layout
    
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
    
    def get_params(self) -> PrimerParams:
        """从界面获取参数"""
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
            CustomMessageBox.show_error(self, "参数错误", f"参数格式不正确：{str(e)}")
            return None
    
    def reset_to_default(self):
        """重置为默认参数"""
        from PyQt5.QtWidgets import QMessageBox
        reply = CustomMessageBox.show_question(
            self,
            "确认重置",
            "确定要将参数重置为默认值吗？"
        )
        if reply == QMessageBox.Yes:
            self.set_params(PrimerParams())
    
    def load_template(self):
        """加载模板"""
        from PyQt5.QtWidgets import QInputDialog
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
            else:
                CustomMessageBox.show_error(self, "加载失败", "无法加载模板")
    
    def save_template(self):
        """保存模板"""
        from PyQt5.QtWidgets import QInputDialog
        params = self.get_params()
        if not params:
            return
        
        name, ok = QInputDialog.getText(self, "保存模板", "模板名称:")
        if ok and name:
            if self.template_manager.save_template(name, params):
                CustomMessageBox.show_success(self, "保存成功", f"模板 '{name}' 已保存")
            else:
                CustomMessageBox.show_error(self, "保存失败", "无法保存模板")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f9fafb;
            }
            QLabel {
                color: #374151;
                font-size: 9pt;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 9pt;
                color: #1f2937;
            }
            QLineEdit:hover {
                border-color: #9ca3af;
            }
            QLineEdit:focus {
                border-color: #4f46e5;
                outline: none;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 7px 15px;
                font-weight: 600;
                color: #374151;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #f3f4f6;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
            }
        """)
    
    def accept(self):
        """确认按钮"""
        params = self.get_params()
        if params:
            super().accept()
