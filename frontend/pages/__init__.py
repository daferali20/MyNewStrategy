# frontend/pages/__init__.py
"""
حزمة صفحات التطبيق (Frontend Pages Package)
تصدير كافة دوال عرض الصفحات (Renderers) للوحة التحكم، المسح الآلي، التحليل التفصيلي، ومستكشف الملفات
"""

from frontend.pages.dashboard import render as render_dashboard
from frontend.pages.scanner import render as render_scanner
from frontend.pages.analyze import render as render_analyze
from frontend.pages.file_explorer import render as render_file_explorer

__all__ = [
    'render_dashboard',
    'render_scanner',
    'render_analyze',
    'render_file_explorer'
]
