; Inno Setup 安装脚本
; 引物设计工具 - NCBI Primer-BLAST 自动化工具
; 适配 Windows 7/8/10/11 (64位)

#define MyAppName "引物设计工具"
#define MyAppVersion "3.0"
#define MyAppPublisher "生物信息学工具"
#define MyAppURL "https://github.com/yourusername/primer-design-blast"
#define MyAppExeName "引物设计工具.exe"

[Setup]
; 应用程序信息
AppId={{A5B6C7D8-E9F0-4A1B-8C2D-3E4F5A6B7C8D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 安装路径
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; 许可协议（如果有的话，取消注释）
; LicenseFile=LICENSE.txt

; 输出设置
OutputDir=installer_output
OutputBaseFilename=PrimerDesignBlast_Setup_v{#MyAppVersion}
SetupIconFile=primer_design_blast\resources\icon.ico

; 压缩设置
Compression=lzma2/max
SolidCompression=yes

; Windows 版本要求
MinVersion=6.1sp1
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; 权限设置
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; UI 设置
WizardStyle=modern
DisableWelcomePage=no
ShowLanguageDialog=auto

; 卸载设置
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 主程序文件（PyInstaller打包后的所有文件）
Source: "dist\PrimerDesignBlast\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; README 文档
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

; 使用说明
Source: "exe使用说明.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; 桌面快捷方式（可选）
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 安装完成后运行程序（可选）
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除用户数据（可选，注意：会删除下载的驱动）
Type: filesandordirs; Name: "{localappdata}\PrimerDesignBlast"

[Code]
// 自定义安装前检查
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // 可以在这里添加额外的检查，例如：
  // - 检查是否安装了必要的运行库
  // - 检查磁盘空间
  // - 检查Windows版本
end;

// 安装完成后的自定义操作
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 可以在这里添加安装后的操作，例如：
    // - 创建配置文件
    // - 初始化数据库
  end;
end;

[Messages]
; 自定义消息（中文）
WelcomeLabel2=This will install [name/ver] on your computer.%n%nThis is a professional NCBI Primer-BLAST automation tool for primer design and sequence analysis.%n%nIt is recommended that you close all other applications before continuing.
FinishedHeadingLabel=Completing the [name] Setup Wizard
FinishedLabelNoIcons=Setup has finished installing [name] on your computer.
ClickFinish=Click Finish to exit Setup.
FinishedLabel=Setup has finished installing [name] on your computer. The application may be launched by selecting the installed icons.
