# -*- coding: utf-8 -*-
"""
浏览器驱动自动更新服务
支持自动检测浏览器版本并下载匹配的驱动程序
"""

import os
import platform
import logging
import subprocess
import winreg
import zipfile
import requests
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from ..utils.resource_utils import get_resource_path


@dataclass
class BrowserInfo:
    """浏览器信息"""
    name: str  # Edge 或 Chrome
    version: str  # 版本号
    driver_url: str  # 驱动下载地址
    driver_path: str  # 驱动保存路径


class DriverUpdater:
    """浏览器驱动更新器"""
    
    # Edge 驱动下载 API
    EDGE_DRIVER_API = "https://msedgedriver.azureedge.net"
    
    # Chrome 驱动下载 API
    CHROME_DRIVER_API = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    CHROME_DRIVER_DOWNLOAD = "https://storage.googleapis.com/chrome-for-testing-public"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system()
        self.release = platform.release()
        
    def get_edge_version(self) -> Optional[str]:
        """
        获取 Edge 浏览器版本号
        
        Returns:
            版本号字符串，如 "120.0.2210.121"，未找到返回 None
        """
        try:
            if self.system != "Windows":
                self.logger.warning("仅支持 Windows 系统")
                return None
            
            # 方法1: 读取注册表
            try:
                key_path = r"SOFTWARE\Microsoft\Edge\BLBeacon"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                self.logger.info(f"从注册表获取 Edge 版本: {version}")
                return version
            except WindowsError:
                pass
            
            # 方法2: 查找安装目录
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
            
            for edge_path in edge_paths:
                if os.path.exists(edge_path):
                    # 使用 wmic 获取版本
                    result = subprocess.run(
                        ['wmic', 'datafile', 'where', f'name="{edge_path}"', 'get', 'Version', '/value'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Version=' in line:
                                version = line.split('=')[1].strip()
                                self.logger.info(f"从文件版本获取 Edge 版本: {version}")
                                return version
            
            self.logger.warning("未找到 Edge 浏览器")
            return None
            
        except Exception as e:
            self.logger.error(f"获取 Edge 版本失败: {e}")
            return None
    
    def get_chrome_version(self) -> Optional[str]:
        """
        获取 Chrome 浏览器版本号
        
        Returns:
            版本号字符串，如 "120.0.6099.109"，未找到返回 None
        """
        try:
            if self.system != "Windows":
                self.logger.warning("仅支持 Windows 系统")
                return None
            
            # 方法1: 读取注册表
            try:
                key_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                self.logger.info(f"从注册表获取 Chrome 版本: {version}")
                return version
            except WindowsError:
                pass
            
            # 方法2: 查找安装目录
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    # 使用 wmic 获取版本
                    result = subprocess.run(
                        ['wmic', 'datafile', 'where', f'name="{chrome_path}"', 'get', 'Version', '/value'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Version=' in line:
                                version = line.split('=')[1].strip()
                                self.logger.info(f"从文件版本获取 Chrome 版本: {version}")
                                return version
            
            self.logger.warning("未找到 Chrome 浏览器")
            return None
            
        except Exception as e:
            self.logger.error(f"获取 Chrome 版本失败: {e}")
            return None
    
    def get_edge_driver_url(self, version: str) -> Optional[str]:
        """
        根据 Edge 版本号获取驱动下载地址
        
        Args:
            version: Edge 版本号
            
        Returns:
            驱动下载 URL
        """
        try:
            # Edge 驱动命名规则: edgedriver_win64.zip 或 edgedriver_win32.zip
            arch = "64" if platform.machine().endswith('64') else "32"
            
            # 构建下载 URL
            url = f"{self.EDGE_DRIVER_API}/{version}/edgedriver_win{arch}.zip"
            
            # 验证 URL 是否有效
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                self.logger.info(f"找到 Edge 驱动: {url}")
                return url
            else:
                self.logger.warning(f"Edge 驱动 URL 无效: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取 Edge 驱动 URL 失败: {e}")
            return None
    
    def get_chrome_driver_url(self, version: str) -> Optional[str]:
        """
        根据 Chrome 版本号获取驱动下载地址
        
        Args:
            version: Chrome 版本号
            
        Returns:
            驱动下载 URL
        """
        try:
            # 获取主版本号（前三位）
            major_version = '.'.join(version.split('.')[:3])
            
            # 查询可用版本
            response = requests.get(self.CHROME_DRIVER_API, timeout=10)
            if response.status_code != 200:
                self.logger.error(f"无法访问 Chrome 驱动 API: {response.status_code}")
                return None
            
            data = response.json()
            
            # 查找匹配版本
            for version_info in reversed(data.get('versions', [])):
                ver = version_info.get('version', '')
                if ver.startswith(major_version):
                    # 找到匹配版本，获取 Windows 驱动下载链接
                    downloads = version_info.get('downloads', {}).get('chromedriver', [])
                    for download in downloads:
                        if download.get('platform') == 'win64':
                            url = download.get('url')
                            self.logger.info(f"找到 Chrome 驱动: {url}")
                            return url
            
            self.logger.warning(f"未找到匹配的 Chrome 驱动版本: {major_version}")
            return None
            
        except Exception as e:
            self.logger.error(f"获取 Chrome 驱动 URL 失败: {e}")
            return None
    
    def download_driver(
        self, 
        url: str, 
        save_dir: str,
        progress_callback=None
    ) -> bool:
        """
        下载驱动文件
        
        Args:
            url: 下载地址
            save_dir: 保存目录
            progress_callback: 进度回调函数 (current_bytes, total_bytes)
            
        Returns:
            是否下载成功
        """
        try:
            self.logger.info(f"开始下载驱动: {url}")
            
            # 创建保存目录
            os.makedirs(save_dir, exist_ok=True)
            
            # 下载文件
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code != 200:
                self.logger.error(f"下载失败: HTTP {response.status_code}")
                return False
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # 临时文件路径
            temp_file = os.path.join(save_dir, "temp_driver.zip")
            
            # 写入文件
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 回调进度
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            self.logger.info(f"下载完成: {temp_file}")
            
            # 解压文件
            self.logger.info("正在解压驱动...")
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                # 提取所有 .exe 文件
                for member in zip_ref.namelist():
                    if member.endswith('.exe'):
                        # 提取到目标目录，使用正确的文件名
                        filename = os.path.basename(member)
                        source = zip_ref.open(member)
                        target = os.path.join(save_dir, filename)
                        
                        with open(target, 'wb') as f:
                            f.write(source.read())
                        
                        self.logger.info(f"已提取: {target}")
            
            # 删除临时文件
            os.remove(temp_file)
            self.logger.info("驱动更新完成")
            return True
            
        except Exception as e:
            self.logger.error(f"下载驱动失败: {e}")
            return False
    
    def update_edge_driver(self, progress_callback=None) -> Tuple[bool, str]:
        """
        更新 Edge 驱动
        
        Args:
            progress_callback: 进度回调
            
        Returns:
            (是否成功, 消息)
        """
        # 获取浏览器版本
        version = self.get_edge_version()
        if not version:
            return False, "未检测到 Edge 浏览器"
        
        # 获取驱动下载地址
        url = self.get_edge_driver_url(version)
        if not url:
            return False, f"未找到匹配版本 {version} 的驱动"
        
        # 确定保存目录
        driver_dir = "win10" if self.release != "7" else "win7"
        save_path = get_resource_path(f"resources/drivers/{driver_dir}")
        
        # 下载驱动
        success = self.download_driver(url, save_path, progress_callback)
        
        if success:
            return True, f"Edge 驱动已更新到版本 {version}"
        else:
            return False, "驱动下载失败"
    
    def update_chrome_driver(self, progress_callback=None) -> Tuple[bool, str]:
        """
        更新 Chrome 驱动
        
        Args:
            progress_callback: 进度回调
            
        Returns:
            (是否成功, 消息)
        """
        # 获取浏览器版本
        version = self.get_chrome_version()
        if not version:
            return False, "未检测到 Chrome 浏览器"
        
        # 获取驱动下载地址
        url = self.get_chrome_driver_url(version)
        if not url:
            return False, f"未找到匹配版本 {version} 的驱动"
        
        # 确定保存目录
        driver_dir = "win10" if self.release != "7" else "win7"
        save_path = get_resource_path(f"resources/drivers/{driver_dir}")
        
        # 下载驱动
        success = self.download_driver(url, save_path, progress_callback)
        
        if success:
            return True, f"Chrome 驱动已更新到版本 {version}"
        else:
            return False, "驱动下载失败"
    
    def update_all_drivers(self, progress_callback=None) -> Tuple[bool, str]:
        """
        更新所有驱动
        
        Args:
            progress_callback: 进度回调
            
        Returns:
            (是否成功, 消息)
        """
        results = []
        
        # 更新 Edge
        success, msg = self.update_edge_driver(progress_callback)
        results.append(("Edge", success, msg))
        
        # 更新 Chrome
        success, msg = self.update_chrome_driver(progress_callback)
        results.append(("Chrome", success, msg))
        
        # 汇总结果
        success_count = sum(1 for _, success, _ in results if success)
        messages = [f"{name}: {msg}" for name, _, msg in results]
        
        if success_count == len(results):
            return True, "所有驱动更新成功\n" + "\n".join(messages)
        elif success_count > 0:
            return True, f"部分驱动更新成功 ({success_count}/{len(results)})\n" + "\n".join(messages)
        else:
            return False, "所有驱动更新失败\n" + "\n".join(messages)
