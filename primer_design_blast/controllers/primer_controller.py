# -*- coding: utf-8 -*-
"""
引物设计业务控制器
处理核心业务逻辑,协调服务层和视图层
"""

import os
import logging
import time
import threading
from enum import Enum
from typing import Callable, Optional, List, Tuple
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal

from ..models.primer_params import PrimerParams
from ..services.coordinate_service import CoordinateService, CoordinateValidationResult
from ..services.web_automation_service import WebAutomationService
from ..utils.resource_utils import get_resource_path


class TaskState(Enum):
    """任务状态枚举"""
    IDLE = "idle"  # 空闲
    INITIALIZING = "initializing"  # 初始化中
    RUNNING = "running"  # 运行中
    PAUSED = "paused"  # 暂停
    STOPPING = "stopping"  # 停止中
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 错误


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
        
        # 任务控制 - 使用线程锁保护
        self._state_lock = threading.RLock()
        self._task_state = TaskState.IDLE
        self.should_stop = False
        self.stats = ProcessingStats()
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 5  # 秒
    
    @property
    def task_state(self) -> TaskState:
        """获取任务状态（线程安全）"""
        with self._state_lock:
            return self._task_state
    
    @task_state.setter
    def task_state(self, state: TaskState):
        """设置任务状态（线程安全）"""
        with self._state_lock:
            old_state = self._task_state
            self._task_state = state
            self.logger.info(f"任务状态变更: {old_state.value} -> {state.value}")
    
    @property
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.task_state in [TaskState.INITIALIZING, TaskState.RUNNING]
    
    def can_start_new_task(self) -> bool:
        """检查是否可以开始新任务"""
        with self._state_lock:
            return self._task_state in [TaskState.IDLE, TaskState.COMPLETED, TaskState.ERROR]
    
    def initialize_coordinate_service(self, chain_file: Optional[str] = None):
        """
        初始化坐标转换服务
        
        Args:
            chain_file: chain文件路径,如果为None则自动查找
            
        Raises:
            RuntimeError: 如果坐标转换器初始化失败
        """
        if chain_file is None:
            chain_file = get_resource_path("resources/hg19ToHg38/hg19ToHg38.over.chain")
        
        self.coord_service = CoordinateService(chain_file)
        
        # 检查坐标转换器是否真的初始化成功
        if self.coord_service.liftover is None:
            error_msg = (
                f"坐标转换器初始化失败!\n"
                f"链文件路径: {chain_file}\n"
                f"文件存在: {os.path.exists(chain_file)}\n"
                f"请检查:\n"
                f"1. chain 文件是否损坏\n"
                f"2. pyliftover 模块是否正确安装\n"
                f"3. 查看日志获取详细错误信息"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        self.logger.info(f"坐标转换服务已初始化: {chain_file}")
    
    def validate_input(
        self, 
        input_text: str, 
        genome_version: str
    ) -> Tuple[List[CoordinateValidationResult], List[CoordinateValidationResult]]:
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
        # 检查是否可以启动新任务
        if not self.can_start_new_task():
            self.logger.warning(f"无法启动新任务，当前状态: {self.task_state.value}")
            self.error_occurred.emit(
                "任务冲突",
                f"当前任务状态为 {self.task_state.value}，请等待当前任务完成"
            )
            return
        
        # 设置状态为初始化中
        self.task_state = TaskState.INITIALIZING
        self.should_stop = False
        self.task_started.emit()
        
        try:
            # 初始化服务
            if not self.coord_service:
                try:
                    self.initialize_coordinate_service()
                except RuntimeError as e:
                    self.logger.error(f"坐标转换服务初始化失败: {e}")
                    self.error_occurred.emit(
                        "初始化失败",
                        f"坐标转换服务初始化失败:\n{str(e)}\n\n"
                        f"如果不需要坐标转换功能，请选择 hg38/GRCh38 基因组版本。"
                    )
                    self.task_state = TaskState.ERROR
                    return
            
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
                    self.task_state = TaskState.ERROR
                    return
            else:
                # 跳过验证,直接解析
                valid_results = self._parse_without_validation(input_text)
                if not valid_results:
                    self.error_occurred.emit(
                        "没有有效数据",
                        "未能解析到任何有效坐标"
                    )
                    self.task_state = TaskState.ERROR
                    return
            
            # 初始化统计
            self.stats = ProcessingStats(total=len(valid_results))
            self.stats_updated.emit(self.stats)
            
            # 确保浏览器已启动
            if not self._ensure_browser_ready(browser):
                self.task_state = TaskState.ERROR
                return
            
            # 设置状态为运行中
            self.task_state = TaskState.RUNNING
            
            # 处理每个坐标
            self.progress_updated.emit(
                f"开始处理 {self.stats.total} 组数据"
            )
            
            for result in valid_results:
                # 检查停止信号
                if self.should_stop:
                    self.logger.info("用户请求停止任务")
                    self.progress_updated.emit("用户取消操作")
                    self.task_state = TaskState.IDLE
                    self.task_stopped.emit()
                    return
                
                # 检查浏览器状态
                if not self.web_service.ensure_driver_alive():
                    self.logger.error("浏览器已关闭，尝试重启")
                    if not self._ensure_browser_ready(browser):
                        self.logger.error("浏览器重启失败，终止任务")
                        self.error_occurred.emit(
                            "浏览器错误",
                            "浏览器已关闭且无法重启，请手动重新开始"
                        )
                        self.task_state = TaskState.ERROR
                        return
                
                # 处理单个坐标（带重试）
                self._process_single_coordinate_with_retry(
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
                self.task_state = TaskState.COMPLETED
                self.task_completed.emit(self.stats)
        
        except Exception as e:
            self.logger.error(f"批量处理出错: {e}", exc_info=True)
            self.error_occurred.emit("处理错误", f"发生异常: {str(e)}")
            self.task_state = TaskState.ERROR
        
        finally:
            # 确保状态被正确设置
            if self.task_state == TaskState.RUNNING:
                self.task_state = TaskState.IDLE
    
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
    
    def _ensure_browser_ready(self, browser: str) -> bool:
        """
        确保浏览器已就绪
        
        Args:
            browser: 浏览器类型
            
        Returns:
            是否就绪
        """
        try:
            # 检查浏览器是否存活
            if self.web_service.ensure_driver_alive():
                self.logger.info("浏览器已就绪")
                return True
            
            # 启动浏览器
            self.progress_updated.emit(f"正在启动 {browser} 浏览器...")
            if not self.web_service.setup_driver(browser):
                self.error_occurred.emit(
                    "浏览器启动失败",
                    f"无法启动 {browser} 浏览器，请检查驱动程序"
                )
                return False
            
            # 打开页面并验证元素
            self.progress_updated.emit("正在打开Primer-BLAST页面...")
            if not self.web_service.open_primer_blast():
                self.error_occurred.emit(
                    "页面打开失败",
                    "无法打开 Primer-BLAST 页面"
                )
                return False
            
            # 自动验证页面元素
            self.progress_updated.emit("正在验证网页元素...")
            try:
                if self.web_service.page and hasattr(self.web_service.page, 'validate_page_elements'):
                    validation_success = self.web_service.page.validate_page_elements()
                    if validation_success:
                        self.progress_updated.emit("✓ 网页元素验证通过")
                    else:
                        self.progress_updated.emit("⚠ 部分元素定位异常,将使用备用策略")
            except Exception as e:
                self.logger.warning(f"页面验证失败: {e}")
                self.progress_updated.emit("⚠ 页面验证出错,继续执行")
            
            return True
            
        except Exception as e:
            self.logger.error(f"浏览器准备失败: {e}", exc_info=True)
            self.error_occurred.emit("浏览器错误", f"浏览器准备失败: {str(e)}")
            return False
    
    def _process_single_coordinate_with_retry(
        self,
        result: CoordinateValidationResult,
        genome_version: str,
        params: PrimerParams
    ):
        """
        处理单个坐标（带重试机制）
        
        Args:
            result: 坐标验证结果
            genome_version: 基因组版本
            params: 引物参数
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    self.progress_updated.emit(
                        f"[{result.line_number}] 重试 {attempt}/{self.max_retries-1}"
                    )
                    time.sleep(self.retry_delay * attempt)  # 指数退避
                
                # 尝试处理
                success = self._process_single_coordinate(result, genome_version, params)
                
                if success:
                    return  # 成功则返回
                else:
                    last_error = "处理失败"
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(
                    f"[{result.line_number}] 第 {attempt + 1} 次尝试失败: {e}"
                )
        
        # 所有重试都失败
        self.progress_updated.emit(
            f"[{result.line_number}] 处理失败（已重试 {self.max_retries} 次）: {last_error}"
        )
        self.stats.failed += 1
    
    def _process_single_coordinate(
        self,
        result: CoordinateValidationResult,
        genome_version: str,
        params: PrimerParams
    ) -> bool:
        """
        处理单个坐标
        
        Args:
            result: 坐标验证结果
            genome_version: 基因组版本
            params: 引物参数
            
        Returns:
            是否成功
        """
        try:
            self.progress_updated.emit(
                f"[{result.line_number}] 处理: {result.chromosome}:{result.position}"
            )
            
            chrom = result.chromosome
            pos = result.position
            
            # 坐标转换
            if genome_version == "hg19/GRCh37":
                self.progress_updated.emit("正在转换 hg19 → hg38...")
                
                # 检查坐标服务是否可用
                if not self.coord_service:
                    error_msg = "坐标转换服务未初始化(coord_service为None)"
                    self.logger.error(error_msg)
                    self.progress_updated.emit(f"坐标转换失败: {error_msg}")
                    return False
                
                if not self.coord_service.liftover:
                    error_msg = "坐标转换器未初始化(liftover为None)"
                    self.logger.error(error_msg)
                    self.progress_updated.emit(f"坐标转换失败: {error_msg}")
                    return False
                
                chrom, pos, error = self.coord_service.convert_hg19_to_hg38(chrom, pos)
                
                if error:
                    self.progress_updated.emit(f"坐标转换失败: {error}")
                    return False
                
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
                return False
            
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
                return True
            else:
                self.progress_updated.emit(
                    f"[{result.line_number}] 处理失败: {error}"
                )
                return False
        
        except Exception as e:
            self.logger.error(f"处理坐标时出错: {e}", exc_info=True)
            self.progress_updated.emit(f"处理出错: {str(e)}")
            return False
    
    def stop_processing(self):
        """停止处理（线程安全）"""
        with self._state_lock:
            if self._task_state in [TaskState.RUNNING, TaskState.INITIALIZING]:
                self.should_stop = True
                self._task_state = TaskState.STOPPING
                self.progress_updated.emit("正在停止任务...")
                self.logger.info("用户请求停止任务")
            else:
                self.logger.warning(f"无法停止任务，当前状态: {self._task_state.value}")
    
    def close_browser(self):
        """关闭浏览器（安全关闭）"""
        try:
            if self.is_running:
                self.logger.warning("任务运行中，建议先停止任务再关闭浏览器")
            
            self.web_service.close_driver()
            self.progress_updated.emit("浏览器已关闭")
            self.logger.info("浏览器已关闭")
        except Exception as e:
            self.logger.error(f"关闭浏览器时出错: {e}", exc_info=True)
