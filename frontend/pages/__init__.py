# frontend/pages/__init__.py
"""
صفحات التطبيق - تم إزالة مستكشف الملفات
"""

from .dashboard import render as render_dashboard
from .scanner import render as render_scanner
from .analyze import render as render_analyze

__all__ = [
    'render_dashboard',
    'render_scanner',
    'render_analyze'
]
