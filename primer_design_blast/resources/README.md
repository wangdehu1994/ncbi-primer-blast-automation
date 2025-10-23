# 资源文件说明

本目录包含引物设计套件运行所需的资源文件。

## 目录结构

```
resources/
├── drivers/              # 浏览器驱动文件
│   ├── win10/           # Windows 10 驱动
│   │   ├── msedgedriver.exe
│   │   └── chromedriver.exe
│   └── win7/            # Windows 7 驱动
│       ├── msedgedriver.exe
│       └── chromedriver.exe
├── hg19ToHg38/          # 基因组坐标转换
│   └── hg19ToHg38.over.chain
└── icon.ico             # 应用程序图标
```

## 文件说明

### 浏览器驱动 (drivers/)

用于 Selenium 自动化控制浏览器访问 NCBI Primer-BLAST 网站。

- **msedgedriver.exe**: Microsoft Edge 浏览器驱动
- **chromedriver.exe**: Google Chrome 浏览器驱动

根据系统版本自动选择：
- Windows 10 及以上：使用 `drivers/win10/`
- Windows 7：使用 `drivers/win7/`

### 坐标转换文件 (hg19ToHg38/)

- **hg19ToHg38.over.chain**: UCSC LiftOver 链文件
  - 用途：将 hg19 基因组坐标转换为 hg38
  - 来源：UCSC Genome Browser
  - 格式：Chain 格式

### 应用图标 (icon.ico)

应用程序窗口和任务栏显示的图标文件。

## 更新说明

### 驱动更新

浏览器驱动需要与浏览器版本匹配。如果遇到版本不兼容问题：

1. 查看浏览器版本：
   - Edge: 设置 > 关于 Microsoft Edge
   - Chrome: 设置 > 关于 Chrome

2. 下载对应驱动：
   - Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
   - Chrome: https://chromedriver.chromium.org/

3. 替换对应目录下的驱动文件

### 坐标转换文件更新

如需支持其他版本转换（如 hg38 to hg19），可从 UCSC 下载相应的 chain 文件：
https://hgdownload.cse.ucsc.edu/goldenpath/hg38/liftOver/

## 注意事项

1. 驱动文件必须是可执行文件（.exe）
2. 坐标转换文件必须是标准的 UCSC chain 格式
3. 图标文件必须是 .ico 格式
4. 不要修改目录结构，代码中的路径已硬编码
