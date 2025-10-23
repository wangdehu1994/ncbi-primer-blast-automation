# -*- coding: utf-8 -*-
"""
引物设计业务控制器
处理核心业务逻辑,协调服务层和视图层
"""

import logging
import time
from typing import Callable, Optional, List
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal

from ..models.primer_params import PrimerParams
from ..services.coordinate_service import CoordinateService, CoordinateValidationResult
from ..services.web_automation_service import WebAutomationService
from ..utils.resource_utils import get_resource_path


@dataclass
class ProcessingStats:
    """处理统计信息"""
    total: int = 0
    processed: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    
    @property
    def remaining(self) -> int:
        return self.total - self.processed
    
    @property
    def progress_percent(self) -> int:
        if self.total == 0:
            return 0
        return int((self.processed / self.total) * 100)


class PrimerController(QObject):
    """引物设计控制器"""
    
    # 信号定义
    progress_updated = pyqtSignal(str)  # 进度文案
    stats_updated = pyqtSignal(ProcessingStats)  # 统计信息更新
    task_started = pyqtSignal()
    task_completed = pyqtSignal(ProcessingStats)
    task_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str, str)  # (title, message)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # 服务实例
        self.coord_service = None
        self.web_service = WebAutomationService()
        
        # 任务控制
        self.is_running = False
        self.should_stop = False
        self.stats = ProcessingStats()
    
    def initialize_coordinate_service(self, chain_file: Optional[str] = None):
        """
        初始化坐标转换服务
        
        Args:
            chain_file: chain文件路径,如果为None则自动查找
        """
        if chain_file is None:
            chain_file = get_resource_path("resources/hg19ToHg38/hg19ToHg38.over.chain")
        
        self.coord_service = CoordinateService(chain_file)
        self.logger.info("坐标转换服务已初始化")
    
    def validate_input(
        self, 
        input_text: str, 
        genome_version: str
    ) -> tuple[List[CoordinateValidationResult], List[CoordinateValidationResult]]:
        """
        验证输入坐标
        
        Args:
            input_text: 输入文本
            genome_version: 基因组版本
            
        Returns:
            (valid_results, invalid_results)
        """
        if not self.coord_service:
            self.initialize_coordinate_service()
        
        return self.coord_service.validate_coordinates_batch(input_text, genome_version)
    
    def start_batch_processing(
        self,
        input_text: str,
        genome_version: str,
        browser: str,
        params: PrimerParams,
        skip_validation: bool = False
    ):
        """
        开始批量处理
        
        Args:
            input_text: 输入文本
            genome_version: 基因组版本
            browser: 浏览器类型
            params: 引物参数
            skip_validation: 是否跳过预验证
        """
        if self.is_running:
            self.logger.warning("任务正在运行中")
            return
        
        self.is_running = True
        self.should_stop = False
        self.task_started.emit()
        
        try:
            # 初始化服务
            if not self.coord_service:
                self.initialize_coordinate_service()
            
            # 预验证坐标
            if not skip_validation:
                self.progress_updated.emit("正在验证输入坐标...")
                valid_results, invalid_results = self.validate_input(input_text, genome_version)
                
                if invalid_results:
                    self.logger.warning(f"发现 {len(invalid_results)} 个无效坐标")
                
                if not valid_results:
                    self.error_occurred.emit(
                        "没有有效数据",
                        "所有输入的坐标都无效，请检查输入格式"
                    )
                    self.is_running = False
                    return
            else:
                # 跳过验证,直接解析
                valid_results = self._parse_without_validation(input_text)
            
            # 初始化统计
            self.stats = ProcessingStats(total=len(valid_results))
            self.stats_updated.emit(self.stats)
            
            # 启动浏览器
            self.progress_updated.emit(f"正在启动 {browser} 浏览器...")
            if not self.web_service.setup_driver(browser):
                self.error_occurred.emit(
                    "浏览器启动失败",
                    f"无法启动 {browser} 浏览器，请检查驱动程序"
                )
                self.is_running = False
                return
            
            # 处理每个坐标
            self.progress_updated.emit(
                f"开始处理 {self.stats.total} 组数据"
            )
            
            for result in valid_results:
                if self.should_stop:
                    self.progress_updated.emit("用户取消操作")
                    self.task_stopped.emit()
                    break
                
                self._process_single_coordinate(
                    result,
                    genome_version,
                    params
                )
                
                # 更新统计
                self.stats.processed += 1
                self.stats_updated.emit(self.stats)
                
                # 避免请求过快
                time.sleep(2)
            
            # 完成
            if not self.should_stop:
                self.progress_updated.emit("所有任务处理完成!")
                self.task_completed.emit(self.stats)
        
        except Exception as e:
            self.logger.error(f"批量处理出错: {e}", exc_info=True)
            self.error_occurred.emit("处理错误", str(e))
        
        finally:
            self.is_running = False
    
    def _parse_without_validation(self, input_text: str) -> List[CoordinateValidationResult]:
        """不验证直接解析（用于跳过验证模式）"""
        results = []
        for idx, line in enumerate(input_text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                chrom = parts[0].lower().replace("chr", "")
                try:
                    pos = int(parts[1])
                    results.append(CoordinateValidationResult(
                        line_number=idx,
                        original_line=line,
                        is_valid=True,
                        chromosome=chrom,
                        position=pos
                    ))
                except:
                    pass
        
        return results
    
    def _process_single_coordinate(
        self,
        result: CoordinateValidationResult,
        genome_version: str,
        params: PrimerParams
    ):
        """处理单个坐标"""
        try:
            self.progress_updated.emit(
                f"[{result.line_number}] 处理: {result.chromosome}:{result.position}"
            )
            
            chrom = result.chromosome
            pos = result.position
            
            # 坐标转换
            if genome_version == "hg19/GRCh37":
                self.progress_updated.emit("正在转换 hg19 → hg38...")
                chrom, pos, error = self.coord_service.convert_hg19_to_hg38(chrom, pos)
                
                if error:
                    self.progress_updated.emit(f"坐标转换失败: {error}")
                    self.stats.failed += 1
                    return
                
                self.progress_updated.emit(
                    f"转换成功: {result.chromosome}:{result.position} → {chrom}:{pos}"
                )
                genome_version = "hg38/GRCh38"
            
            # 获取Accession
            accession = self.coord_service.get_accession(chrom, genome_version)
            if not accession:
                self.progress_updated.emit(
                    f"无法获取 {chrom} 的Accession编号"
                )
                self.stats.failed += 1
                return
            
            self.progress_updated.emit(f"Accession: {accession}")
            
            # 提交到Primer-BLAST
            self.progress_updated.emit("正在提交到 Primer-BLAST...")
            success, error = self.web_service.submit_primer_design(
                accession,
                pos,
                params
            )
            
            if success:
                self.progress_updated.emit(
                    f"[{result.line_number}] 处理成功"
                )
                self.stats.success += 1
            else:
                self.progress_updated.emit(
                    f"[{result.line_number}] 处理失败: {error}"
                )
                self.stats.failed += 1
        
        except Exception as e:
            self.logger.error(f"处理坐标时出错: {e}", exc_info=True)
            self.progress_updated.emit(f"处理出错: {str(e)}")
            self.stats.failed += 1
    
    def stop_processing(self):
        """停止处理"""
        if self.is_running:
            self.should_stop = True
            self.progress_updated.emit("正在停止任务...")
    
    def close_browser(self):
        """关闭浏览器"""
        self.web_service.close_driver()
        self.progress_updated.emit("浏览器已关闭")
