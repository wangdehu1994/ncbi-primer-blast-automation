# -*- coding: utf-8 -*-
"""
Web自动化服务
使用页面对象模式管理Primer-BLAST网页操作
"""

import time
import logging
import threading
import platform
from typing import Optional, Tuple
from contextlib import contextmanager

try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        NoSuchElementException, 
        TimeoutException,
        WebDriverException
    )
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    logging.error("Selenium模块未安装，网页自动化功能将不可用")

from ..models.config import AppConfig
from ..models.primer_params import PrimerParams
from ..utils.resource_utils import get_resource_path
from .element_locator import ElementLocator


class PrimerBlastPage:
    """Primer-BLAST页面对象"""
    
    def __init__(self, driver, config: AppConfig):
        self.driver = driver
        self.config = config
        self.selectors = config.WEB_SELECTORS
        self.logger = logging.getLogger(__name__)
        # 使用智能元素定位器
        self.locator = ElementLocator(driver)
    
    def wait_for_element(self, by: By, value: str, timeout: int = 20):
        """等待元素可见"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 20):
        """等待元素可点击"""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def click_one_target_tab(self):
        """点击单目标标签"""
        tab = self.locator.find_element('one_target_tab', wait_clickable=True)
        if tab:
            ActionChains(self.driver).move_to_element(tab).click().perform()
            self.logger.debug("已切换到单目标模式")
        else:
            raise Exception("无法定位到单目标标签")
    
    def click_advanced_button(self):
        """点击高级设置按钮"""
        button = self.locator.find_element('advanced_button', wait_clickable=True)
        if button:
            button.click()
            self.logger.debug("已打开高级设置")
        else:
            raise Exception("无法定位到高级设置按钮")
    
    def set_sequence_id(self, accession: str):
        """设置序列ID"""
        seq_box = self.locator.find_element('seq_input')
        if seq_box:
            seq_box.clear()
            seq_box.send_keys(str(accession))
            self.logger.debug(f"已设置序列ID: {accession}")
        else:
            raise Exception("无法定位到序列输入框")
    
    def set_pcr_product_size(self, min_size: int, max_size: int):
        """设置PCR产物大小"""
        pcr_min = self.locator.find_element('pcr_min')
        pcr_max = self.locator.find_element('pcr_max')
        if pcr_min and pcr_max:
            pcr_min.clear()
            pcr_min.send_keys(str(min_size))
            pcr_max.clear()
            pcr_max.send_keys(str(max_size))
            self.logger.debug(f"已设置PCR产物大小: {min_size}-{max_size}")
        else:
            raise Exception("无法定位到PCR产物大小输入框")
    
    def set_tm_values(self, tm_min: float, tm_opt: float, tm_max: float, tm_diff: int):
        """设置Tm值"""
        tm_min_elem = self.locator.find_element('tm_min')
        tm_opt_elem = self.locator.find_element('tm_opt')
        tm_max_elem = self.locator.find_element('tm_max')
        tm_diff_elem = self.locator.find_element('tm_max_diff')
        
        if all([tm_min_elem, tm_opt_elem, tm_max_elem, tm_diff_elem]):
            tm_min_elem.clear()
            tm_min_elem.send_keys(str(tm_min))
            tm_opt_elem.clear()
            tm_opt_elem.send_keys(str(tm_opt))
            tm_max_elem.clear()
            tm_max_elem.send_keys(str(tm_max))
            tm_diff_elem.clear()
            tm_diff_elem.send_keys(str(tm_diff))
            self.logger.debug(f"已设置Tm值: {tm_min}/{tm_opt}/{tm_max}, 差值:{tm_diff}")
        else:
            raise Exception("无法定位到Tm值输入框")
    
    def set_primer_size(self, min_size: int, opt_size: int, max_size: int):
        """设置引物大小"""
        self.driver.find_element(By.ID, self.selectors['primer_min_size']).clear()
        self.driver.find_element(By.ID, self.selectors['primer_min_size']).send_keys(str(min_size))
        self.driver.find_element(By.ID, self.selectors['primer_opt_size']).clear()
        self.driver.find_element(By.ID, self.selectors['primer_opt_size']).send_keys(str(opt_size))
        self.driver.find_element(By.ID, self.selectors['primer_max_size']).clear()
        self.driver.find_element(By.ID, self.selectors['primer_max_size']).send_keys(str(max_size))
        self.logger.debug(f"已设置引物大小: {min_size}/{opt_size}/{max_size}")
    
    def set_other_parameters(self, params: PrimerParams):
        """设置其他参数"""
        # 返回引物数量
        self.driver.find_element(By.ID, self.selectors['primer_num_return']).clear()
        self.driver.find_element(By.ID, self.selectors['primer_num_return']).send_keys(
            str(params.primer_num_return)
        )
        
        # 最大连续碱基
        self.driver.find_element(By.ID, self.selectors['poly_x']).clear()
        self.driver.find_element(By.ID, self.selectors['poly_x']).send_keys(str(params.max_poly_x))
        
        # 3'端最大GC
        self.driver.find_element(By.ID, self.selectors['end_gc_max']).clear()
        self.driver.find_element(By.ID, self.selectors['end_gc_max']).send_keys(
            str(params.end_gc_max)
        )
        self.logger.debug("已设置其他参数")
    
    def set_database_and_organism(self):
        """设置数据库和物种"""
        # 设置数据库
        db_dropdown = Select(self.driver.find_element(By.ID, self.selectors['database']))
        db_dropdown.select_by_value("PRIMERDB/genome_selected_species")
        
        # 设置物种
        organism_box = self.driver.find_element(By.ID, self.selectors['organism'])
        organism_box.clear()
        organism_box.send_keys("Homo sapiens")
        self.logger.debug("已设置数据库和物种")
    
    def set_snp_and_window_options(self):
        """设置SNP和新窗口选项"""
        # 设置SNP选项
        try:
            label_snp = self.wait_for_clickable(By.XPATH, "//label[@for='NO_SNP']", timeout=10)
            label_snp.click()
        except:
            self.logger.warning("无法设置SNP选项")
        
        # 设置新窗口选项
        try:
            new_web_label = self.wait_for_clickable(By.XPATH, "//label[@for='nw2']", timeout=10)
            new_web_label.click()
        except:
            self.logger.warning("无法设置新窗口选项")
        
        self.logger.debug("已设置SNP和窗口选项")
    
    def set_primer_range(self, position: int, ext_left: int, ext_right: int):
        """设置引物取值范围"""
        left_start = max(1, position - ext_left)
        left_end = max(1, position - 20)
        right_start = position + 20
        right_end = position + ext_right
        
        self.driver.find_element(By.ID, self.selectors['primer5_start']).clear()
        self.driver.find_element(By.ID, self.selectors['primer5_start']).send_keys(str(left_start))
        self.driver.find_element(By.ID, self.selectors['primer5_end']).clear()
        self.driver.find_element(By.ID, self.selectors['primer5_end']).send_keys(str(left_end))
        self.driver.find_element(By.ID, self.selectors['primer3_start']).clear()
        self.driver.find_element(By.ID, self.selectors['primer3_start']).send_keys(str(right_start))
        self.driver.find_element(By.ID, self.selectors['primer3_end']).clear()
        self.driver.find_element(By.ID, self.selectors['primer3_end']).send_keys(str(right_end))
        
        self.logger.debug(f"已设置引物范围: 左({left_start}-{left_end}), 右({right_start}-{right_end})")
    
    def submit_form(self) -> str:
        """提交表单并返回新标签页句柄"""
        old_handles = self.driver.window_handles
        
        submit_btn = self.locator.find_element('submit_button', wait_clickable=True)
        if submit_btn:
            submit_btn.click()
            self.logger.info("表单已提交")
        else:
            raise Exception("无法定位到提交按钮")
        
        # 等待新标签页
        WebDriverWait(self.driver, 15).until(lambda drv: len(drv.window_handles) > len(old_handles))
        time.sleep(1)
        
        new_handles = self.driver.window_handles
        diff = set(new_handles) - set(old_handles)
        
        if diff:
            return diff.pop()
        return None
    
    def validate_page_elements(self) -> bool:
        """验证页面关键元素是否可定位"""
        self.logger.info("开始验证页面元素...")
        results = self.locator.validate_all_elements(timeout=5)
        
        critical_elements = [
            'seq_input', 'one_target_tab', 'pcr_min', 'pcr_max',
            'submit_button'
        ]
        
        for elem in critical_elements:
            if not results.get(elem, False):
                self.logger.error(f"关键元素 '{elem}' 无法定位,页面可能已变更")
                return False
        
        self.logger.info("页面元素验证通过")
        return True


class WebAutomationService:
    """Web自动化服务（单例模式）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        self.driver = None
        self.page = None
        self.page_initialized = False
        self.current_browser = None
        
        # 初始化驱动路径
        self._init_driver_paths()
        self._initialized = True
    
    def _init_driver_paths(self):
        """初始化浏览器驱动路径"""
        system = platform.system()
        release = platform.release()
        driver_dir = "resources/drivers/win10"
        
        if system == "Windows" and release == "7":
            driver_dir = "resources/drivers/win7"
        
        self.driver_paths = {
            "Edge": get_resource_path(f"{driver_dir}/msedgedriver.exe"),
            "Chrome": get_resource_path(f"{driver_dir}/chromedriver.exe"),
        }
        
        self.logger.info(f"驱动路径: {self.driver_paths}")
    
    def ensure_driver_alive(self) -> bool:
        """检查驱动是否存活"""
        if not self.driver:
            return False
        
        try:
            _ = self.driver.current_url
            return True
        except:
            self.logger.warning("检测到浏览器已关闭")
            self.driver = None
            self.page_initialized = False
            return False
    
    def setup_driver(self, browser: str = "Edge") -> bool:
        """
        设置浏览器驱动
        
        Args:
            browser: 浏览器类型 (Edge/Chrome)
            
        Returns:
            是否成功
        """
        if self.driver and self.ensure_driver_alive():
            if self.current_browser == browser:
                return True
            else:
                self.close_driver()
        
        try:
            if browser == "Edge":
                options = EdgeOptions()
                service = EdgeService(executable_path=self.driver_paths["Edge"])
            elif browser == "Chrome":
                options = ChromeOptions()
                service = ChromeService(executable_path=self.driver_paths["Chrome"])
            else:
                raise ValueError(f"不支持的浏览器: {browser}")
            
            # 通用选项
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_argument("--incognito")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--log-level=3")
            
            # 创建驱动
            if browser == "Edge":
                self.driver = webdriver.Edge(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(service=service, options=options)
            
            self.current_browser = browser
            self.page = PrimerBlastPage(self.driver, self.config)
            
            self.logger.info(f"{browser} 浏览器驱动启动成功")
            return True
            
        except Exception as e:
            self.logger.error(f"{browser} 浏览器驱动启动失败: {e}")
            return False
    
    def close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("浏览器已关闭")
            except:
                pass
            finally:
                self.driver = None
                self.page = None
                self.page_initialized = False
                self.current_browser = None
    
    def open_primer_blast(self) -> bool:
        """
        打开Primer-BLAST网页
        
        Returns:
            是否成功打开
        """
        if not self.driver:
            self.logger.error("浏览器驱动未启动")
            return False
        
        try:
            self.logger.info("正在打开 Primer-BLAST 网页...")
            self.driver.get(self.config.PRIMER_BLAST_URL)
            
            # 等待页面加载
            WebDriverWait(self.driver, self.config.PAGE_LOAD_TIMEOUT).until(
                EC.url_contains("primer-blast")
            )
            
            # 刷新data:URL
            if "data:" in self.driver.current_url:
                self.driver.refresh()
            
            WebDriverWait(self.driver, self.config.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            
            self.logger.info("Primer-BLAST 网页已打开")
            return True
            
        except Exception as e:
            self.logger.error(f"打开网页失败: {e}")
            return False
    
    def initialize_page(self, params: PrimerParams) -> Tuple[bool, Optional[str]]:
        """
        初始化Primer-BLAST页面（只执行一次）
        
        Args:
            params: 引物参数
            
        Returns:
            (success, error_message)
        """
        if not self.driver:
            return False, "浏览器驱动未启动"
        
        try:
            # 如果当前不在Primer-BLAST页面,则跳转到该页面
            current_url = self.driver.current_url
            if "primer-blast" not in current_url.lower():
                self.logger.info("正在加载 Primer-BLAST 网页...")
                self.driver.get(self.config.PRIMER_BLAST_URL)
                
                # 等待页面加载
                WebDriverWait(self.driver, self.config.PAGE_LOAD_TIMEOUT).until(
                    EC.url_contains("primer-blast")
                )
                
                # 刷新data:URL
                if "data:" in self.driver.current_url:
                    self.driver.refresh()
                
                WebDriverWait(self.driver, self.config.PAGE_LOAD_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
            
            self.logger.info("正在配置 Primer-BLAST 参数...")
            
            # 切换到单目标模式
            self.page.click_one_target_tab()
            
            # 打开高级设置
            self.page.click_advanced_button()
            
            # 设置所有固定参数
            self.page.set_pcr_product_size(params.pcr_min, params.pcr_max)
            self.page.set_tm_values(
                params.tm_min, 
                params.tm_opt, 
                params.tm_max, 
                params.tm_max_difference
            )
            self.page.set_primer_size(
                params.primer_min_size,
                params.primer_opt_size,
                params.primer_max_size
            )
            self.page.set_other_parameters(params)
            self.page.set_database_and_organism()
            self.page.set_snp_and_window_options()
            
            self.page_initialized = True
            self.logger.info("Primer-BLAST 页面初始化完成")
            return True, None
            
        except Exception as e:
            error_msg = f"页面初始化失败: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def submit_primer_design(
        self,
        accession: str,
        position: int,
        params: PrimerParams,
        max_retries: int = 3
    ) -> Tuple[bool, Optional[str]]:
        """
        提交引物设计任务（带重试）
        
        Args:
            accession: 序列Accession号
            position: 坐标位置
            params: 引物参数
            max_retries: 最大重试次数
            
        Returns:
            (success, error_message)
        """
        if not self.ensure_driver_alive():
            return False, "浏览器已关闭，请重新启动"
        
        # 首次需要初始化页面
        if not self.page_initialized:
            success, error = self.initialize_page(params)
            if not success:
                return False, error
        
        for attempt in range(max_retries):
            try:
                # 设置序列ID
                self.page.set_sequence_id(accession)
                
                # 设置引物范围
                self.page.set_primer_range(
                    position,
                    params.extension_left,
                    params.extension_right
                )
                
                # 获取原始窗口句柄
                old_handle = self.driver.current_window_handle
                
                # 提交表单
                new_tab = self.page.submit_form()
                
                # 切换回原窗口
                if new_tab:
                    try:
                        self.driver.switch_to.window(old_handle)
                        self.logger.info("已切换回原页面")
                    except Exception as e:
                        self.logger.warning(f"切换回原页面失败: {e}")
                
                return True, None
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * self.config.RETRY_DELAY
                    self.logger.warning(
                        f"第 {attempt + 1} 次尝试失败，{wait_time}秒后重试: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    error_msg = f"重试 {max_retries} 次后仍然失败: {str(e)}"
                    self.logger.error(error_msg)
                    return False, error_msg
        
        return False, "未知错误"
