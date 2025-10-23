# -*- coding: utf-8 -*-
"""
引物参数数据模型
使用pydantic进行参数验证
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class PrimerParams(BaseModel):
    """引物设计参数模型"""
    
    # PCR产物大小
    pcr_min: int = Field(default=100, ge=50, le=30000, description="PCR产物最小长度")
    pcr_max: int = Field(default=1200, ge=50, le=30000, description="PCR产物最大长度")
    
    # Tm值设置
    tm_min: float = Field(default=58.0, gt=30, lt=95, description="最小Tm值")
    tm_opt: float = Field(default=60.0, gt=30, lt=95, description="最佳Tm值")
    tm_max: float = Field(default=62.0, gt=30, lt=95, description="最大Tm值")
    tm_max_difference: int = Field(default=2, ge=0, le=10, description="最大Tm差值")
    
    # 引物大小
    primer_min_size: int = Field(default=18, ge=10, le=40, description="引物最小碱基数")
    primer_opt_size: int = Field(default=20, ge=10, le=40, description="引物最佳碱基数")
    primer_max_size: int = Field(default=25, ge=10, le=40, description="引物最大碱基数")
    
    # 其他参数
    primer_num_return: int = Field(default=10, ge=1, le=50, description="返回引物数量")
    end_gc_max: int = Field(default=4, ge=0, le=5, description="引物3'端最大GC")
    max_poly_x: int = Field(default=4, ge=0, le=10, description="最大连续碱基数")
    
    # 扩展长度
    extension_left: int = Field(default=800, ge=0, description="位点左侧扩展长度")
    extension_right: int = Field(default=800, ge=0, description="位点右侧扩展长度")
    
    @validator('pcr_max')
    def pcr_max_must_be_greater_than_min(cls, v, values):
        """验证PCR最大值必须大于最小值"""
        if 'pcr_min' in values and v <= values['pcr_min']:
            raise ValueError(f'PCR最大值({v})必须大于最小值({values["pcr_min"]})')
        return v
    
    @validator('tm_opt')
    def tm_opt_must_be_in_range(cls, v, values):
        """验证最佳Tm值必须在最小和最大值之间"""
        if 'tm_min' in values and v <= values['tm_min']:
            raise ValueError(f'最佳Tm值({v})必须大于最小Tm值({values["tm_min"]})')
        return v
    
    @validator('tm_max')
    def tm_max_must_be_greater_than_opt(cls, v, values):
        """验证最大Tm值必须大于最佳值"""
        if 'tm_opt' in values and v <= values['tm_opt']:
            raise ValueError(f'最大Tm值({v})必须大于最佳Tm值({values["tm_opt"]})')
        return v
    
    @validator('tm_max_difference')
    def tm_difference_must_be_valid(cls, v, values):
        """验证Tm差值不能超过范围"""
        if 'tm_min' in values and 'tm_max' in values:
            tm_range = values['tm_max'] - values['tm_min']
            if v > tm_range:
                raise ValueError(f'最大Tm差值({v})不能超过Tm范围({tm_range})')
        return v
    
    @validator('primer_opt_size')
    def primer_opt_must_be_in_range(cls, v, values):
        """验证最佳引物大小在范围内"""
        if 'primer_min_size' in values and v < values['primer_min_size']:
            raise ValueError(f'最佳引物大小({v})不能小于最小值({values["primer_min_size"]})')
        return v
    
    @validator('primer_max_size')
    def primer_max_must_be_greater_than_opt(cls, v, values):
        """验证最大引物大小"""
        if 'primer_opt_size' in values and v < values['primer_opt_size']:
            raise ValueError(f'最大引物大小({v})不能小于最佳值({values["primer_opt_size"]})')
        return v
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PrimerParams':
        """从字典创建"""
        return cls(**data)
    
    class Config:
        """Pydantic配置"""
        validate_assignment = True  # 赋值时也进行验证
        extra = 'forbid'  # 禁止额外字段
