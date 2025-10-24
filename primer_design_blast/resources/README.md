# 资源文件说明# 资源文件说明



本目录包含引物设计工具运行所需的资源文件。本目录包含引物设计工具运行所需的资源文件。



## 目录结构## 目录结构



``````

resources/resources/

├── drivers/              # 浏览器驱动文件├── drivers/              # 浏览器驱动文件

│   ├── msedgedriver.exe│   ├── win10/           # Windows 10 驱动

│   └── chromedriver.exe│   │   ├── msedgedriver.exe

└── hg19ToHg38/          # 基因组坐标转换文件│   │   └── chromedriver.exe

    └── hg19ToHg38.over.chain│   └── win7/            # Windows 7 驱动

```│       ├── msedgedriver.exe

│       └── chromedriver.exe

## 文件说明├── hg19ToHg38/          # 基因组坐标转换

│   └── hg19ToHg38.over.chain

### 浏览器驱动 (drivers/)└── icon.ico             # 应用程序图标

```

用于 Selenium 自动化控制浏览器访问 NCBI Primer-BLAST 网站。

## 文件说明

- **msedgedriver.exe**: Microsoft Edge 浏览器驱动

- **chromedriver.exe**: Google Chrome 浏览器驱动### 浏览器驱动 (drivers/)



**更新方法**：用于 Selenium 自动化控制浏览器访问 NCBI Primer-BLAST 网站。

- 在程序菜单栏：工具 → 更新浏览器驱动

- 程序会自动下载与浏览器版本匹配的驱动- **msedgedriver.exe**: Microsoft Edge 浏览器驱动

- **chromedriver.exe**: Google Chrome 浏览器驱动

### 坐标转换文件 (hg19ToHg38/)

根据系统版本自动选择：

- **hg19ToHg38.over.chain**: UCSC LiftOver 链文件- Windows 10 及以上：使用 `drivers/win10/`

  - 用途：将 hg19 基因组坐标转换为 hg38- Windows 7：使用 `drivers/win7/`

  - 来源：UCSC Genome Browser

### 坐标转换文件 (hg19ToHg38/)

**下载方法**：

- 在程序菜单栏：工具 → 下载坐标转换文件- **hg19ToHg38.over.chain**: UCSC LiftOver 链文件

- 程序会自动下载并保存到正确位置  - 用途：将 hg19 基因组坐标转换为 hg38

  - 来源：UCSC Genome Browser

## 注意事项  - 格式：Chain 格式



1. 如果使用 hg38 坐标，无需下载转换文件### 应用图标 (icon.ico)

2. 驱动版本需要与浏览器版本匹配，建议使用程序自动更新功能

3. 不要手动修改目录结构应用程序窗口和任务栏显示的图标文件。


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
