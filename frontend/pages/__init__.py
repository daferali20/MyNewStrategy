# frontend/pages/__init__.py
"""
صفحات التطبيق
"""

from .dashboard import render as render_dashboard
from .scanner import render as render_scanner
from .file_explorer import render as render_file_explorer
from .analyze import render as render_analyze

__all__ = [
    'render_dashboard',
    'render_scanner',
    'render_file_explorer',
    'render_analyze'
]
