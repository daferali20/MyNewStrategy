# frontend/utils/__init__.py
"""
أدوات مساعدة للواجهة الأمامية
"""

# استيرادات بسيطة لتجنب الدائرية
from .helpers import (
    load_css,
    load_inline_css,
    format_currency,
    format_percentage,
    format_number,
    format_datetime,
    format_volume,
    get_sample_data,
    get_sample_analysis,
    is_valid_symbol
)

# استيرادات البيانات - يتم استيرادها عند الحاجة
# لتجنب الدائرية، نستوردها بشكل منفصل

__all__ = [
    'load_css',
    'load_inline_css',
    'format_currency',
    'format_percentage',
    'format_number',
    'format_datetime',
    'format_volume',
    'get_sample_data',
    'get_sample_analysis',
    'is_valid_symbol'
]
