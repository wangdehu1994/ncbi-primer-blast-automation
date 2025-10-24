# -*- coding: utf-8 -*-
"""
引物设计工具 (Primer Design Tool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

一个专业的NCBI Primer-BLAST自动化工具

:copyright: (c) 2025
:license: MIT
"""

__version__ = '3.0.0'
__author__ = 'Primer Design Team'

from .models.primer_params import PrimerParams
from .controllers.primer_controller import PrimerController

__all__ = ['PrimerParams', 'PrimerController', '__version__']
