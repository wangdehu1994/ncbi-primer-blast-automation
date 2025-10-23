# -*- coding: utf-8 -*-
"""
应用配置管理
"""

import os
import json
import logging
from typing import Dict, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from .primer_params import PrimerParams


@dataclass
class AppConfig:
    """应用配置类"""
    
    # 应用信息
    APP_NAME: str = "引物设计工具"
    APP_VERSION: str = "3.0"
    
    # 默认参数
    DEFAULT_GENOME_VERSION: str = "hg38/GRCh38"
    DEFAULT_BROWSER: str = "Edge"
    
    # 染色体映射 - hg19/GRCh37
    CHR_MAPPING_HG19: Dict[str, str] = None
    
    # 染色体映射 - hg38/GRCh38
    CHR_MAPPING_HG38: Dict[str, str] = None
    
    # 网页元素定位器
    WEB_SELECTORS: Dict[str, str] = None
    
    # Primer-BLAST URL
    PRIMER_BLAST_URL: str = "https://www.ncbi.nlm.nih.gov/tools/primer-blast"
    
    # 重试配置
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    
    # 浏览器等待时间
    PAGE_LOAD_TIMEOUT: int = 30
    ELEMENT_WAIT_TIMEOUT: int = 20
    
    def __post_init__(self):
        """初始化后处理"""
        if self.CHR_MAPPING_HG19 is None:
            self.CHR_MAPPING_HG19 = {
                "1": "NC_000001.10", "2": "NC_000002.11", "3": "NC_000003.11",
                "4": "NC_000004.11", "5": "NC_000005.9", "6": "NC_000006.11",
                "7": "NC_000007.13", "8": "NC_000008.10", "9": "NC_000009.11",
                "10": "NC_000010.10", "11": "NC_000011.9", "12": "NC_000012.11",
                "13": "NC_000013.10", "14": "NC_000014.8", "15": "NC_000015.9",
                "16": "NC_000016.9", "17": "NC_000017.10", "18": "NC_000018.9",
                "19": "NC_000019.9", "20": "NC_000020.10", "21": "NC_000021.8",
                "22": "NC_000022.10", "x": "NC_000023.10", "23": "NC_000023.10",
                "y": "NC_000024.9", "24": "NC_000024.9"
            }
        
        if self.CHR_MAPPING_HG38 is None:
            self.CHR_MAPPING_HG38 = {
                "1": "NC_000001.11", "2": "NC_000002.12", "3": "NC_000003.12",
                "4": "NC_000004.12", "5": "NC_000005.10", "6": "NC_000006.12",
                "7": "NC_000007.14", "8": "NC_000008.11", "9": "NC_000009.12",
                "10": "NC_000010.11", "11": "NC_000011.10", "12": "NC_000012.12",
                "13": "NC_000013.11", "14": "NC_000014.9", "15": "NC_000015.10",
                "16": "NC_000016.10", "17": "NC_000017.11", "18": "NC_000018.10",
                "19": "NC_000019.10", "20": "NC_000020.11", "21": "NC_000021.9",
                "22": "NC_000022.11", "x": "NC_000023.11", "23": "NC_000023.11",
                "y": "NC_000024.10", "24": "NC_000024.10"
            }
        
        if self.WEB_SELECTORS is None:
            self.WEB_SELECTORS = {
                'seq_input': 'seq',
                'one_target_tab': 'OneTargTab',
                'advanced_button': 'btnDescrOver',
                'pcr_min': 'PRIMER_PRODUCT_MIN',
                'pcr_max': 'PRIMER_PRODUCT_MAX',
                'tm_min': 'PRIMER_MIN_TM',
                'tm_opt': 'PRIMER_OPT_TM',
                'tm_max': 'PRIMER_MAX_TM',
                'tm_max_diff': 'PRIMER_MAX_DIFF_TM',
                'primer_min_size': 'PRIMER_MIN_SIZE',
                'primer_opt_size': 'PRIMER_OPT_SIZE',
                'primer_max_size': 'PRIMER_MAX_SIZE',
                'primer_num_return': 'PRIMER_NUM_RETURN',
                'end_gc_max': 'PRIMER_MAX_END_GC',
                'poly_x': 'POLYX',
                'primer5_start': 'PRIMER5_START',
                'primer5_end': 'PRIMER5_END',
                'primer3_start': 'PRIMER3_START',
                'primer3_end': 'PRIMER3_END',
                'organism': 'ORGANISM',
                'database': 'PRIMER_SPECIFICITY_DATABASE',
                'submit_button': 'input.blastbutton.prbutton'
            }


class TemplateManager:
    """参数模板管理器"""
    
    def __init__(self, templates_file: Optional[str] = None):
        """
        初始化模板管理器
        
        Args:
            templates_file: 模板文件路径,默认为用户目录下的templates.json
        """
        if templates_file is None:
            user_dir = Path.home() / '.primer_design_suite'
            user_dir.mkdir(exist_ok=True)
            templates_file = str(user_dir / 'templates.json')
        
        self.templates_file = templates_file
        self.config_file = str(Path(templates_file).parent / 'config.json')
        self.logger = logging.getLogger(__name__)
    
    def load_templates(self) -> Dict[str, dict]:
        """加载所有模板"""
        if not os.path.exists(self.templates_file):
            return {}
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载模板失败: {e}")
            return {}
    
    def load_config(self) -> Dict[str, any]:
        """加载配置"""
        if not os.path.exists(self.config_file):
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return {}
    
    def save_config(self, config: Dict[str, any]) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return False
    
    def get_default_template(self) -> Optional[str]:
        """获取默认模板名称"""
        config = self.load_config()
        return config.get('default_template', None)
    
    def set_default_template(self, name: Optional[str]) -> bool:
        """设置默认模板"""
        config = self.load_config()
        if name is None:
            config.pop('default_template', None)
        else:
            config['default_template'] = name
        return self.save_config(config)
    
    def save_template(self, name: str, params: PrimerParams) -> bool:
        """
        保存参数模板
        
        Args:
            name: 模板名称
            params: 引物参数对象
            
        Returns:
            是否保存成功
        """
        try:
            templates = self.load_templates()
            templates[name] = params.to_dict()
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"模板 '{name}' 保存成功")
            return True
        except Exception as e:
            self.logger.error(f"保存模板失败: {e}")
            return False
    
    def load_template(self, name: str) -> Optional[PrimerParams]:
        """
        加载指定模板
        
        Args:
            name: 模板名称
            
        Returns:
            引物参数对象,如果不存在返回None
        """
        templates = self.load_templates()
        if name not in templates:
            return None
        
        try:
            return PrimerParams.from_dict(templates[name])
        except Exception as e:
            self.logger.error(f"加载模板 '{name}' 失败: {e}")
            return None
    
    def delete_template(self, name: str) -> bool:
        """
        删除模板
        
        Args:
            name: 模板名称
            
        Returns:
            是否删除成功
        """
        try:
            templates = self.load_templates()
            if name in templates:
                del templates[name]
                
                with open(self.templates_file, 'w', encoding='utf-8') as f:
                    json.dump(templates, f, ensure_ascii=False, indent=2)
                
                # 如果删除的是默认模板,清除默认设置
                if self.get_default_template() == name:
                    self.set_default_template(None)
                
                self.logger.info(f"模板 '{name}' 已删除")
                return True
            return False
        except Exception as e:
            self.logger.error(f"删除模板失败: {e}")
            return False
    
    def get_template_names(self) -> List[str]:
        """获取所有模板名称"""
        templates = self.load_templates()
        return list(templates.keys())
