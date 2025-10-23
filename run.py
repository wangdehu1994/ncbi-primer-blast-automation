# -*- coding: utf-8 -*-
"""
引物设计工具 - 启动入口
Run: python run.py
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入并运行主程序
from primer_design_blast.app import main

if __name__ == "__main__":
    main()
