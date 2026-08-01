# frontend/utils/__init__.py
"""
حزمة الأدوات المساعدة للواجهة الأمامية (Frontend Utilities)
تتيح الاستيراد المباشر لدوال التنسيق، الجلب المؤقت، وإدارة حالة الجلسة
"""

from frontend.utils.helpers import (
    load_css,
    load_inline_css,
    format_currency,
    format_percentage,
    format_number,
    format_datetime,
    format_volume,
    get_sample_data,
    get_sample_analysis,
    is_valid_symbol,
    get_stock_data_cached,
    get_stock_info_cached,
    get_stock_data,
    get_stock_info,
    get_file_content
)

from frontend.utils.state import (
    init_session_state,
    get_state,
    set_state,
    update_state,
    reset_state,
    clear_state
)

__all__ = [
    # دوال Design & Helpers
    'load_css',
    'load_inline_css',
    'format_currency',
    'format_percentage',
    'format_number',
    'format_datetime',
    'format_volume',
    'get_sample_data',
    'get_sample_analysis',
    'is_valid_symbol',
    'get_stock_data_cached',
    'get_stock_info_cached',
    'get_stock_data',
    'get_stock_info',
    'get_file_content',
    
    # دوال State Management
    'init_session_state',
    'get_state',
    'set_state',
    'update_state',
    'reset_state',
    'clear_state'
]
