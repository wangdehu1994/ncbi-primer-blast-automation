# -*- coding: utf-8 -*-
"""
模板管理对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QMessageBox, QInputDialog, QListWidgetItem, QTextEdit, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ...models.config import TemplateManager
from ...models.primer_params import PrimerParams
from .message_box import CustomMessageBox


class TemplateDialog(QDialog):
    """模板管理对话框"""
    
    def __init__(self, template_manager: TemplateManager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.selected_template = None
        
        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("参数模板管理")
        self.setMinimumWidth(650)
        self.setMinimumHeight(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f4f6;
            }
            QLabel {
                color: #1f2937;
                font-weight: 600;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 列表和详情的水平布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        
        # 左侧：模板列表
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0,0,0,0)
        list_layout.setSpacing(8)
        list_layout.addWidget(QLabel("已存模板:"))
        
        self.template_list = QListWidget()
        self.template_list.itemSelectionChanged.connect(self.on_template_selected)
        self.template_list.itemDoubleClicked.connect(self.on_load_and_close)
        list_layout.addWidget(self.template_list)
        
        content_layout.addWidget(list_widget, 2)
        
        # 右侧：模板详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0,0,0,0)
        detail_layout.setSpacing(8)
        detail_layout.addWidget(QLabel("参数预览:"))
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        
        content_layout.addWidget(detail_widget, 3)
        
        layout.addLayout(content_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("加载")
        self.load_btn.setEnabled(False)
        self.load_btn.setObjectName("primary_button")
        self.load_btn.clicked.connect(self.load_selected_template)
        
        self.set_default_btn = QPushButton("设为默认")
        self.set_default_btn.setEnabled(False)
        self.set_default_btn.clicked.connect(self.set_as_default)
        
        self.rename_btn = QPushButton("重命名")
        self.rename_btn.setEnabled(False)
        self.rename_btn.clicked.connect(self.rename_template)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setObjectName("danger_button")
        self.delete_btn.clicked.connect(self.delete_template)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.set_default_btn)
        button_layout.addWidget(self.rename_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # 提示信息
        tip_label = QLabel("💡 双击模板可直接加载 | ⭐ 代表默认模板")
        tip_label.setStyleSheet("color: #6b7785; font-size: 8pt;")
        layout.addWidget(tip_label, 0, Qt.AlignRight)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f4f6;
            }
            QLabel {
                color: #1f2937;
                font-weight: 600;
                font-size: 9pt;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #e0e7ff;
                color: #374151;
            }
            QListWidget::item:hover:!selected {
                background-color: #f9fafb;
            }
            QTextEdit {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                color: #374151;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px 14px;
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
            QPushButton:disabled {
                background-color: #f3f4f6;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
            QPushButton#primary_button {
                background-color: #4f46e5;
                color: #ffffff;
                border: none;
            }
            QPushButton#primary_button:hover {
                background-color: #4338ca;
            }
            QPushButton#primary_button:disabled {
                background-color: #a5b4fc;
                border: none;
            }
            QPushButton#danger_button {
                background-color: #dc2626;
                color: #ffffff;
                border: none;
            }
            QPushButton#danger_button:hover {
                background-color: #b91c1c;
            }
            QPushButton#danger_button:disabled {
                background-color: #fca5a5;
                border: none;
            }
        """)
    
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        names = self.template_manager.get_template_names()
        default_template = self.template_manager.get_default_template()
        
        if not names:
            item = QListWidgetItem("(暂无模板)")
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(Qt.gray)
            self.template_list.addItem(item)
        else:
            for name in names:
                display_name = f"⭐ {name}" if name == default_template else name
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, name)
                self.template_list.addItem(item)
    
    def on_template_selected(self):
        """模板选择改变"""
        current_item = self.template_list.currentItem()
        
        if current_item and current_item.data(Qt.UserRole):
            self.load_btn.setEnabled(True)
            self.set_default_btn.setEnabled(True)
            self.rename_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            
            template_name = current_item.data(Qt.UserRole)
            params = self.template_manager.load_template(template_name)
            
            if params:
                details = self.format_params_details(params)
                self.detail_text.setPlainText(details)
        else:
            self.load_btn.setEnabled(False)
            self.set_default_btn.setEnabled(False)
            self.rename_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.detail_text.clear()
    
    def format_params_details(self, params: PrimerParams) -> str:
        """格式化参数详情"""
        return (
            f"PCR产物: {params.pcr_min} - {params.pcr_max} bp\n"
            f"Tm: {params.tm_min} - {params.tm_max} °C (Opt: {params.tm_opt}, Diff: {params.tm_max_difference})\n"
            f"引物大小: {params.primer_min_size} - {params.primer_max_size} bp (Opt: {params.primer_opt_size})\n"
            f"返回数量: {params.primer_num_return}\n"
            f"3'端最大GC: {params.end_gc_max}\n"
            f"最大连续碱基: {params.max_poly_x}\n"
            f"序列扩展: {params.extension_left} (左), {params.extension_right} (右) bp"
        )
    
    def load_selected_template(self):
        """加载选中的模板"""
        current_item = self.template_list.currentItem()
        if current_item:
            self.selected_template = current_item.data(Qt.UserRole)
            self.accept()
    
    def on_load_and_close(self, item: QListWidgetItem):
        """双击加载并关闭"""
        if item.data(Qt.UserRole):
            self.selected_template = item.data(Qt.UserRole)
            self.accept()
    
    def set_as_default(self):
        """设置为默认模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        template_name = current_item.data(Qt.UserRole)
        current_default = self.template_manager.get_default_template()
        
        if template_name == current_default:
            reply = CustomMessageBox.show_question(
                self, "取消默认", f"'{template_name}' 已是默认模板，要取消吗？"
            )
            if reply == QMessageBox.Yes:
                self.template_manager.set_default_template(None)
                self.load_templates()
        else:
            if self.template_manager.set_default_template(template_name):
                self.load_templates()
                CustomMessageBox.show_success(
                    self, "设置成功", f"'{template_name}' 已设为默认模板。"
                )
    
    def rename_template(self):
        """重命名模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.data(Qt.UserRole)
        new_name, ok = QInputDialog.getText(
            self, "重命名模板", "新名称:", text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            if new_name in self.template_manager.get_template_names():
                CustomMessageBox.show_error(self, "重命名失败", f"模板 '{new_name}' 已存在。")
                return
            
            params = self.template_manager.load_template(old_name)
            if params and self.template_manager.save_template(new_name, params):
                self.template_manager.delete_template(old_name)
                self.load_templates()
    
    def delete_template(self):
        """删除模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        template_name = current_item.data(Qt.UserRole)
        reply = CustomMessageBox.show_question(
            self, "确认删除", f"确定要删除模板 '{template_name}' 吗？"
        )
        
        if reply == QMessageBox.Yes:
            if self.template_manager.delete_template(template_name):
                self.load_templates()
                self.detail_text.clear()
    
    def get_selected_template(self):
        """获取选中的模板名称"""
        return self.selected_template
