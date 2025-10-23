# 引物设计套件 v3.0

## 简介

引物设计套件是一个专业的NCBI Primer-BLAST自动化工具，用于批量设计PCR引物。

### 主要功能

- ✅ 批量处理染色体坐标
- ✅ 自动坐标转换（hg19 → hg38）
- ✅ 参数模板管理
- ✅ 任务进度跟踪
- ✅ 错误重试机制
- ✅ 友好的图形界面

## 安装

### 依赖要求

```bash
pip install -r requirements.txt
```

### 必需依赖

- Python 3.8+
- PyQt5
- selenium
- pydantic
- pyliftover

## 使用方法

### 1. 启动程序

**方式1: 使用启动脚本（推荐）**
```bash
# 从Primer_Design_Blast目录
双击 "启动引物设计套件.bat"
```

**方式2: 命令行启动**
```bash
# 从Primer_Design_Blast目录运行
python run.py
```

**方式3: 作为模块运行**
```bash
# 从Primer_Design_Blast目录运行
python -m primer_design_suite.app
```

或者运行打包后的exe文件。

### 2. 输入坐标

在输入区域填写染色体坐标，格式：

```
chr1 123456
chr2 234567
X 345678
```

### 3. 配置参数

设置引物设计参数，或加载已保存的模板。

### 4. 开始设计

点击"开始设计引物"按钮，程序会自动处理所有坐标。

## 目录结构

```
primer_design_suite/
├── app.py                 # 主程序入口
├── models/                # 数据模型
│   ├── primer_params.py   # 引物参数模型
│   └── config.py          # 配置管理
├── views/                 # 视图层
│   ├── main_window.py     # 主窗口
│   └── components/        # UI组件
├── controllers/           # 控制器
│   └── primer_controller.py
├── services/              # 服务层
│   ├── coordinate_service.py
│   └── web_automation_service.py
└── utils/                 # 工具模块
    ├── logger.py
    └── resource_utils.py
```

## 配置文件

参数模板保存在：
- Windows: `C:\Users\{用户名}\.primer_design_suite\templates.json`
- Linux/Mac: `~/.primer_design_suite/templates.json`

## 注意事项

1. 需要安装对应版本的浏览器驱动（Edge或Chrome）
2. hg19坐标转换需要chain文件
3. 首次使用建议先用少量数据测试

## 更新日志

### v3.0.0 (2025-10-23)

- 🎉 全新架构，采用MVC设计模式
- ✨ 新增菜单栏功能
- ✨ 参数模板管理
- ✨ 批量坐标验证
- ✨ 任务进度统计
- ✨ 停止/恢复功能
- 🐛 修复多项已知问题
- 🚀 性能优化

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
