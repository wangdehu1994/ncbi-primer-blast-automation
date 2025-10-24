# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
用于将 Python 项目打包成 Windows 可执行文件

使用方法：
1. 确保已安装 PyInstaller: pip install pyinstaller
2. 在项目根目录执行: pyinstaller build.spec
3. 生成的 exe 文件位于 dist/ 目录

兼容性：支持 Windows 7/8/10/11 (64位)
"""

block_cipher = None

a = Analysis(
    # 入口文件
    ['run.py'],
    
    # 额外的搜索路径
    pathex=[],
    
    # 二进制文件（DLL等）
    binaries=[],
    
    # 数据文件（资源文件）
    datas=[
        # 包含整个 resources 目录
        ('primer_design_blast/resources', 'primer_design_blast/resources'),
        # 包含 README 文档
        ('README.md', '.'),
        # 如果有其他资源文件，在此添加
        # ('使用说明.md', '.'),
    ],
    
    # 隐式导入的模块（PyInstaller 可能检测不到的）
    hiddenimports=[
        # Selenium WebDriver 相关
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.edge',
        'selenium.webdriver.edge.service',
        'selenium.webdriver.edge.options',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.common',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.action_chains',
        'selenium.webdriver.support',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common',
        'selenium.common.exceptions',
        
        # PyQt5 GUI 相关
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        
        # 网络请求相关
        'requests',
        'urllib3',
        'urllib.request',
        
        # 其他依赖
        'gzip',
        'zipfile',
        'threading',
        'logging',
        'json',
        'pathlib',
    ],
    
    # Hook 文件路径
    hookspath=[],
    
    # Hook 配置
    hooksconfig={},
    
    # 运行时 Hook
    runtime_hooks=[],
    
    # 排除的模块（减小文件大小）
    excludes=[
        # 测试框架
        'pytest',
        'unittest',
        '_pytest',
        
        # 不使用的 GUI 框架
        'tkinter',
        '_tkinter',
        'Tkinter',
        
        # 图像处理库
        'PIL',
        'pillow',
        
        # 其他大型库
        'IPython',
        'jupyter',
        'notebook',
        'matplotlib',
    ],
    
    # Windows 相关设置
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    
    # 加密设置（None 表示不加密）
    cipher=block_cipher,
    
    # 是否不创建归档
    noarchive=False,
)

# Python 字节码归档
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    
    # 程序名称
    name='引物设计工具',
    
    # 调试模式（发布时设为 False）
    debug=False,
    
    # 引导加载器设置
    bootloader_ignore_signals=False,
    
    # 是否去除符号表
    strip=False,
    
    # 是否使用 UPX 压缩（需要安装 UPX）
    upx=True,
    
    # UPX 排除列表
    upx_exclude=[],
    
    # 运行时临时目录
    runtime_tmpdir=None,
    
    # 是否显示控制台窗口（False = 无窗口模式，适合 GUI 程序）
    console=False,
    
    # 禁用窗口化回溯
    disable_windowed_traceback=False,
    
    # 是否模拟命令行参数
    argv_emulation=False,
    
    # 目标架构（None = 自动检测）
    target_arch=None,
    
    # 代码签名标识（需要证书）
    codesign_identity=None,
    
    # 授权文件
    entitlements_file=None,
    
    # 应用图标（.ico 文件）
    icon='primer_design_blast/resources/icon.ico',
)

# 如果使用 --onedir 模式，取消注释下面的 COLLECT 部分
# 并注释掉上面 EXE 中的 a.binaries, a.zipfiles, a.datas
"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='引物设计工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='primer_design_blast/resources/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='引物设计工具'
)
"""
