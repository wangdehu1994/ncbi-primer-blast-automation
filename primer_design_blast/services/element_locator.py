# -*- coding: utf-8 -*-
"""
网站元素定位策略
提供多种备用定位方案,应对网站变更
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


@dataclass
class LocatorStrategy:
    """定位策略"""
    by: str  # By.ID, By.NAME, By.CSS_SELECTOR, By.XPATH等
    value: str  # 定位值
    description: str = ""  # 策略描述


class ElementLocator:
    """智能元素定位器"""
    
    def __init__(self, driver: 'WebDriver'):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        
        # 定义每个元素的多种定位策略(优先级从高到低)
        self.locator_strategies: Dict[str, List[LocatorStrategy]] = {
            'seq_input': [
                LocatorStrategy(By.ID, 'seq', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'seq', '备用1: NAME定位'),
                LocatorStrategy(By.CSS_SELECTOR, 'textarea[name="seq"]', '备用2: CSS选择器'),
                LocatorStrategy(By.XPATH, '//textarea[@id="seq"]', '备用3: XPath'),
            ],
            'one_target_tab': [
                LocatorStrategy(By.ID, 'OneTargTab', '主要: ID定位'),
                LocatorStrategy(By.XPATH, '//a[@id="OneTargTab"]', '备用1: XPath'),
                LocatorStrategy(By.CSS_SELECTOR, 'a#OneTargTab', '备用2: CSS选择器'),
                LocatorStrategy(By.LINK_TEXT, 'Pick primer', '备用3: 链接文本'),
            ],
            'advanced_button': [
                LocatorStrategy(By.ID, 'btnDescrOver', '主要: ID定位'),
                LocatorStrategy(By.CLASS_NAME, 'jig-ncbiinpagenav', '备用1: CLASS定位'),
                LocatorStrategy(By.XPATH, '//button[@id="btnDescrOver"]', '备用2: XPath'),
                LocatorStrategy(By.CSS_SELECTOR, 'button#btnDescrOver', '备用3: CSS选择器'),
            ],
            'pcr_min': [
                LocatorStrategy(By.ID, 'PRIMER_PRODUCT_MIN', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_PRODUCT_MIN', '备用1: NAME定位'),
                LocatorStrategy(By.CSS_SELECTOR, 'input[name="PRIMER_PRODUCT_MIN"]', '备用2: CSS选择器'),
            ],
            'pcr_max': [
                LocatorStrategy(By.ID, 'PRIMER_PRODUCT_MAX', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_PRODUCT_MAX', '备用1: NAME定位'),
                LocatorStrategy(By.CSS_SELECTOR, 'input[name="PRIMER_PRODUCT_MAX"]', '备用2: CSS选择器'),
            ],
            'tm_min': [
                LocatorStrategy(By.ID, 'PRIMER_MIN_TM', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_MIN_TM', '备用1: NAME定位'),
            ],
            'tm_opt': [
                LocatorStrategy(By.ID, 'PRIMER_OPT_TM', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_OPT_TM', '备用1: NAME定位'),
            ],
            'tm_max': [
                LocatorStrategy(By.ID, 'PRIMER_MAX_TM', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_MAX_TM', '备用1: NAME定位'),
            ],
            'tm_max_diff': [
                LocatorStrategy(By.ID, 'PRIMER_MAX_DIFF_TM', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_MAX_DIFF_TM', '备用1: NAME定位'),
            ],
            'primer_min_size': [
                LocatorStrategy(By.ID, 'PRIMER_MIN_SIZE', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_MIN_SIZE', '备用1: NAME定位'),
            ],
            'primer_opt_size': [
                LocatorStrategy(By.ID, 'PRIMER_OPT_SIZE', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_OPT_SIZE', '备用1: NAME定位'),
            ],
            'primer_max_size': [
                LocatorStrategy(By.ID, 'PRIMER_MAX_SIZE', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_MAX_SIZE', '备用1: NAME定位'),
            ],
            'primer_num_return': [
                LocatorStrategy(By.ID, 'PRIMER_NUM_RETURN', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_NUM_RETURN', '备用1: NAME定位'),
            ],
            'end_gc_max': [
                LocatorStrategy(By.ID, 'PRIMER_MAX_END_GC', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_MAX_END_GC', '备用1: NAME定位'),
            ],
            'poly_x': [
                LocatorStrategy(By.ID, 'POLYX', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'POLYX', '备用1: NAME定位'),
            ],
            'primer5_start': [
                LocatorStrategy(By.ID, 'PRIMER5_START', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER5_START', '备用1: NAME定位'),
            ],
            'primer5_end': [
                LocatorStrategy(By.ID, 'PRIMER5_END', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER5_END', '备用1: NAME定位'),
            ],
            'primer3_start': [
                LocatorStrategy(By.ID, 'PRIMER3_START', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER3_START', '备用1: NAME定位'),
            ],
            'primer3_end': [
                LocatorStrategy(By.ID, 'PRIMER3_END', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER3_END', '备用1: NAME定位'),
            ],
            'organism': [
                LocatorStrategy(By.ID, 'ORGANISM', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'ORGANISM', '备用1: NAME定位'),
            ],
            'database': [
                LocatorStrategy(By.ID, 'PRIMER_SPECIFICITY_DATABASE', '主要: ID定位'),
                LocatorStrategy(By.NAME, 'PRIMER_SPECIFICITY_DATABASE', '备用1: NAME定位'),
            ],
            'submit_button': [
                LocatorStrategy(By.CSS_SELECTOR, 'input.blastbutton.prbutton', '主要: CSS类选择器'),
                LocatorStrategy(By.XPATH, '//input[@type="submit" and @class="blastbutton prbutton"]', '备用1: XPath'),
                LocatorStrategy(By.CSS_SELECTOR, 'input[type="submit"].prbutton', '备用2: CSS选择器'),
                LocatorStrategy(By.XPATH, '//input[@value="Get Primers"]', '备用3: 按钮文本'),
            ],
        }
    
    def find_element(
        self, 
        element_key: str, 
        timeout: int = 10,
        wait_clickable: bool = False
    ) -> Optional['WebElement']:
        """
        使用多种策略查找元素
        
        Args:
            element_key: 元素键名
            timeout: 超时时间(秒)
            wait_clickable: 是否等待元素可点击
            
        Returns:
            找到的元素,如果所有策略都失败返回None
        """
        strategies = self.locator_strategies.get(element_key, [])
        
        if not strategies:
            self.logger.warning(f"元素 '{element_key}' 没有定义定位策略")
            return None
        
        for strategy in strategies:
            try:
                self.logger.debug(f"尝试定位 '{element_key}': {strategy.description}")
                
                if wait_clickable:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((strategy.by, strategy.value))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((strategy.by, strategy.value))
                    )
                
                self.logger.info(f"✓ 成功定位 '{element_key}': {strategy.description}")
                return element
                
            except (NoSuchElementException, TimeoutException) as e:
                self.logger.debug(f"✗ 定位失败: {strategy.description} - {str(e)[:50]}")
                continue
            except Exception as e:
                self.logger.error(f"定位元素时发生错误: {e}", exc_info=True)
                continue
        
        self.logger.error(f"所有策略均失败,无法定位元素: '{element_key}'")
        return None
    
    def add_strategy(self, element_key: str, strategy: LocatorStrategy):
        """添加新的定位策略"""
        if element_key not in self.locator_strategies:
            self.locator_strategies[element_key] = []
        self.locator_strategies[element_key].append(strategy)
        self.logger.info(f"已为 '{element_key}' 添加新策略: {strategy.description}")
    
    def validate_all_elements(self, timeout: int = 5) -> Dict[str, bool]:
        """
        验证所有关键元素是否可定位
        
        Args:
            timeout: 每个元素的超时时间
            
        Returns:
            元素名称到验证结果的映射
        """
        results = {}
        
        for element_key in self.locator_strategies.keys():
            element = self.find_element(element_key, timeout=timeout)
            results[element_key] = element is not None
        
        # 统计
        total = len(results)
        success = sum(1 for v in results.values() if v)
        
        self.logger.info(f"元素验证完成: {success}/{total} 成功")
        
        if success < total:
            failed = [k for k, v in results.items() if not v]
            self.logger.warning(f"以下元素定位失败: {', '.join(failed)}")
        
        return results
