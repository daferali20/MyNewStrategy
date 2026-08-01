# frontend/__init__.py
"""
وحدة الواجهة الأمامية (Frontend Package)
توفير الاستيرادات الرئيسية الموحدة للواجهة بشكل آمن ومستقر لتجنب أخطاء Circular Import
"""

from frontend.utils.helpers import (
    load_css,
    load_inline_css,
    format_currency,
    format_percentage,
    format_number,
    format_datetime
)
from frontend.utils.state import (
    init_session_state,
    get_state,
    set_state,
    update_state,
    reset_state
)

__all__ = [
    # Design & Formatting Helpers
    'load_css',
    'load_inline_css',
    'format_currency',
    'format_percentage',
    'format_number',
    'format_datetime',
    
    # State Management Functions
    'init_session_state',
    'get_state',
    'set_state',
    'update_state',
    'reset_state'
]
