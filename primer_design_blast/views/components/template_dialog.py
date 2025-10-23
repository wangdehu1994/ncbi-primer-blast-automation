# -*- coding: utf-8 -*-
"""
模板管理对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QMessageBox, QInputDialog, QListWidgetItem, QTextEdit
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
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("📋 管理引物参数模板")
        title.setFont(QFont("", 14, QFont.Bold))
        title.setStyleSheet("color: #2f3d4c; padding: 10px;")
        layout.addWidget(title)
        
        # 列表和详情的水平布局
        content_layout = QHBoxLayout()
        
        # 左侧：模板列表
        list_layout = QVBoxLayout()
        list_label = QLabel("已保存的模板:")
        list_label.setStyleSheet("font-weight: 600; color: #4f5d6d;")
        list_layout.addWidget(list_label)
        
        self.template_list = QListWidget()
        self.template_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #c9d4e5;
                border-radius: 6px;
                background-color: #fdfefe;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #e7efff;
                color: #2f3d4c;
            }
            QListWidget::item:hover {
                background-color: #f0f5ff;
            }
        """)
        self.template_list.itemSelectionChanged.connect(self.on_template_selected)
        self.template_list.itemDoubleClicked.connect(self.on_load_and_close)
        list_layout.addWidget(self.template_list)
        
        content_layout.addLayout(list_layout, 3)
        
        # 右侧：模板详情
        detail_layout = QVBoxLayout()
        detail_label = QLabel("模板参数预览:")
        detail_label.setStyleSheet("font-weight: 600; color: #4f5d6d;")
        detail_layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #c9d4e5;
                border-radius: 6px;
                background-color: #f7f9fc;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #2f3d4c;
            }
        """)
        detail_layout.addWidget(self.detail_text)
        
        content_layout.addLayout(detail_layout, 2)
        
        layout.addLayout(content_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("📂 加载并应用")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.load_selected_template)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c9aff;
                color: #ffffff;
                font-weight: 600;
                border-radius: 6px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3d86e0;
            }
            QPushButton:disabled {
                background-color: #d5dde7;
                color: #8a96a5;
            }
        """)
        
        self.set_default_btn = QPushButton("⭐ 设为默认")
        self.set_default_btn.setEnabled(False)
        self.set_default_btn.clicked.connect(self.set_as_default)
        self.set_default_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffa940;
                color: #ffffff;
                font-weight: 600;
                border-radius: 6px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #fa8c16;
            }
            QPushButton:disabled {
                background-color: #d5dde7;
                color: #8a96a5;
            }
        """)
        
        self.rename_btn = QPushButton("✏️ 重命名")
        self.rename_btn.setEnabled(False)
        self.rename_btn.clicked.connect(self.rename_template)
        self.rename_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                color: #4f5d6d;
                border-radius: 6px;
                padding: 8px 16px;
                border: 1px solid #d0d7de;
            }
            QPushButton:hover {
                background-color: #e7eaef;
            }
            QPushButton:disabled {
                background-color: #f5f6f8;
                color: #b0b8c0;
            }
        """)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_template)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff7875;
                color: #ffffff;
                font-weight: 600;
                border-radius: 6px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e06764;
            }
            QPushButton:disabled {
                background-color: #d5dde7;
                color: #8a96a5;
            }
        """)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                color: #4f5d6d;
                border-radius: 6px;
                padding: 8px 16px;
                border: 1px solid #d0d7de;
            }
            QPushButton:hover {
                background-color: #e7eaef;
            }
        """)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.set_default_btn)
        button_layout.addWidget(self.rename_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # 提示信息
        tip_label = QLabel("💡 提示：双击模板可直接加载 | ⭐ 星标表示默认模板")
        tip_label.setStyleSheet("color: #6b7785; font-size: 11px; padding: 5px;")
        layout.addWidget(tip_label)
    
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        names = self.template_manager.get_template_names()
        default_template = self.template_manager.get_default_template()
        
        if not names:
            item = QListWidgetItem("(暂无保存的模板)")
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(Qt.gray)
            self.template_list.addItem(item)
        else:
            for name in names:
                # 如果是默认模板,添加星标
                display_name = f"⭐ {name}" if name == default_template else f"📋 {name}"
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, name)
                self.template_list.addItem(item)
    
    def on_template_selected(self):
        """模板选择改变"""
        current_item = self.template_list.currentItem()
        
        if current_item and current_item.data(Qt.UserRole):
            # 启用按钮
            self.load_btn.setEnabled(True)
            self.set_default_btn.setEnabled(True)
            self.rename_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            
            # 显示模板详情
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
        return f"""
模板参数详情
{'=' * 40}

【PCR产物大小】
  最小值: {params.pcr_min} bp
  最大值: {params.pcr_max} bp

【Tm值】
  最小值: {params.tm_min} °C
  最佳值: {params.tm_opt} °C
  最大值: {params.tm_max} °C
  最大差值: {params.tm_max_difference} °C

【引物大小】
  最小值: {params.primer_min_size} bp
  最佳值: {params.primer_opt_size} bp
  最大值: {params.primer_max_size} bp

【其他参数】
  返回引物数: {params.primer_num_return}
  3'端最大GC: {params.end_gc_max}
  最大连续碱基数: {params.max_poly_x}
  左侧扩展: {params.extension_left} bp
  右侧扩展: {params.extension_right} bp
        """.strip()
    
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
        
        # 如果已经是默认模板,则取消默认
        if template_name == current_default:
            reply = CustomMessageBox.show_question(
                self,
                "取消默认",
                f"'{template_name}' 当前是默认模板,是否取消默认设置?"
            )
            if reply == QMessageBox.Yes:
                self.template_manager.set_default_template(None)
                self.load_templates()
                CustomMessageBox.show_success(
                    self,
                    "已取消",
                    "已取消默认模板设置"
                )
        else:
            # 设置为默认
            if self.template_manager.set_default_template(template_name):
                self.load_templates()
                CustomMessageBox.show_success(
                    self,
                    "设置成功",
                    f"'{template_name}' 已设为默认模板\n程序启动时将自动加载此模板"
                )
    
    def rename_template(self):
        """重命名模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.data(Qt.UserRole)
        new_name, ok = QInputDialog.getText(
            self,
            "重命名模板",
            "新的模板名称:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            # 检查新名称是否已存在
            if new_name in self.template_manager.get_template_names():
                CustomMessageBox.show_error(
                    self,
                    "重命名失败",
                    f"模板 '{new_name}' 已存在"
                )
                return
            
            # 加载旧模板
            params = self.template_manager.load_template(old_name)
            if params:
                # 保存为新名称
                if self.template_manager.save_template(new_name, params):
                    # 删除旧模板
                    self.template_manager.delete_template(old_name)
                    # 刷新列表
                    self.load_templates()
                    CustomMessageBox.show_success(
                        self,
                        "重命名成功",
                        f"模板已重命名为 '{new_name}'"
                    )
    
    def delete_template(self):
        """删除模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        template_name = current_item.data(Qt.UserRole)
        reply = CustomMessageBox.show_question(
            self,
            "确认删除",
            f"确定要删除模板 '{template_name}' 吗？"
        )
        
        if reply == QMessageBox.Yes:
            if self.template_manager.delete_template(template_name):
                self.load_templates()
                self.detail_text.clear()
                CustomMessageBox.show_success(
                    self,
                    "删除成功",
                    f"模板 '{template_name}' 已删除"
                )
    
    def get_selected_template(self):
        """获取选中的模板名称"""
        return self.selected_template
