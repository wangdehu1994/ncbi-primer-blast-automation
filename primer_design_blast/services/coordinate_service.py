# -*- coding: utf-8 -*-
"""
坐标转换服务
支持hg19到hg38的坐标转换及批量验证
"""

import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass

try:
    from pyliftover import LiftOver
    HAS_LIFTOVER = True
except ImportError:
    HAS_LIFTOVER = False
    logging.warning("pyliftover模块未安装，坐标转换功能将不可用")

from ..models.config import AppConfig


@dataclass
class CoordinateValidationResult:
    """坐标验证结果"""
    line_number: int
    original_line: str
    is_valid: bool
    chromosome: Optional[str] = None
    position: Optional[int] = None
    error_message: Optional[str] = None


class CoordinateService:
    """坐标转换和验证服务"""
    
    # 支持的染色体
    ALLOWED_CHROMOSOMES = set(str(i) for i in range(1, 25)) | {"x", "y"}
    
    def __init__(self, chain_file: Optional[str] = None):
        """
        初始化坐标服务
        
        Args:
            chain_file: hg19到hg38的chain文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        self.liftover = None
        
        if HAS_LIFTOVER and chain_file:
            try:
                self.liftover = LiftOver(chain_file)
                self.logger.info(f"坐标转换器初始化成功: {chain_file}")
            except Exception as e:
                self.logger.error(f"无法加载坐标转换文件: {e}")
    
    def parse_coordinate_line(self, line: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        解析坐标行
        
        Args:
            line: 输入行,格式: "chr1 123456" 或 "1 123456"
            
        Returns:
            (chromosome, position, error_message)
        """
        line = line.strip()
        if not line:
            return None, None, "空行"
        
        parts = line.split()
        if len(parts) < 2:
            return None, None, f"格式错误:至少需要2列数据(当前:{len(parts)}列)"
        
        # 解析染色体号
        chrom_raw = parts[0].lower().replace("chr", "")
        if chrom_raw not in self.ALLOWED_CHROMOSOMES:
            return None, None, f"不支持的染色体号:{chrom_raw} (支持:1-24,X,Y)"
        
        # 解析位置
        pos_str = parts[1]
        if not pos_str.isdigit():
            return None, None, f"坐标格式错误:{pos_str} (必须为正整数)"
        
        pos_val = int(pos_str)
        if pos_val <= 0:
            return None, None, f"坐标值无效:{pos_val} (必须大于0)"
        
        return chrom_raw, pos_val, None
    
    def validate_coordinates_batch(
        self, 
        lines_text: str, 
        genome_version: str
    ) -> Tuple[List[CoordinateValidationResult], List[CoordinateValidationResult]]:
        """
        批量验证坐标
        
        Args:
            lines_text: 多行坐标文本
            genome_version: 参考基因组版本
            
        Returns:
            (valid_results, invalid_results)
        """
        valid_results = []
        invalid_results = []
        
        for idx, line in enumerate(lines_text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            
            chrom, pos, error = self.parse_coordinate_line(line)
            
            if error:
                invalid_results.append(CoordinateValidationResult(
                    line_number=idx,
                    original_line=line,
                    is_valid=False,
                    error_message=error
                ))
            else:
                valid_results.append(CoordinateValidationResult(
                    line_number=idx,
                    original_line=line,
                    is_valid=True,
                    chromosome=chrom,
                    position=pos
                ))
        
        return valid_results, invalid_results
    
    def convert_hg19_to_hg38(
        self, 
        chromosome: str, 
        position: int
    ) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        将hg19坐标转换为hg38
        
        Args:
            chromosome: 染色体号(不含chr前缀)
            position: 位置
            
        Returns:
            (new_chromosome, new_position, error_message)
        """
        if not self.liftover:
            return None, None, "坐标转换器未初始化"
        
        # 格式化染色体名称
        chrom_formatted = chromosome.lower()
        if not chrom_formatted.startswith("chr"):
            chrom_formatted = "chr" + chrom_formatted
        
        # 标准化X/Y染色体
        if chrom_formatted == "chrx":
            chrom_formatted = "chrX"
        elif chrom_formatted == "chry":
            chrom_formatted = "chrY"
        
        try:
            result = self.liftover.convert_coordinate(chrom_formatted, position)
            
            if result and len(result) > 0:
                new_chrom = result[0][0].replace("chr", "").lower()
                new_pos = int(result[0][1])
                self.logger.info(f"坐标转换成功: {chromosome}:{position} -> {new_chrom}:{new_pos}")
                return new_chrom, new_pos, None
            else:
                error_msg = f"未找到对应的hg38坐标: {chromosome}:{position}"
                self.logger.warning(error_msg)
                return None, None, error_msg
                
        except Exception as e:
            error_msg = f"坐标转换失败: {str(e)}"
            self.logger.error(error_msg)
            return None, None, error_msg
    
    def get_accession(self, chromosome: str, genome_version: str) -> Optional[str]:
        """
        获取染色体的Accession编号
        
        Args:
            chromosome: 染色体号(不含chr前缀)
            genome_version: 参考基因组版本
            
        Returns:
            Accession编号,不存在返回None
        """
        chrom_key = chromosome.strip().lower()
        
        if genome_version == "hg19/GRCh37":
            return self.config.CHR_MAPPING_HG19.get(chrom_key)
        else:  # hg38/GRCh38
            return self.config.CHR_MAPPING_HG38.get(chrom_key)
