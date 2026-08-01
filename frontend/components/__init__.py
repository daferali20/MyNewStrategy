# frontend/components/__init__.py
"""
حزمة مكونات الواجهة (Frontend Components)
تم تنظيم الاستيرادات والتصدير لتوفير وصول سريع ومريح دون التسبب في أخطاء الدائرية (Circular Import)
"""

from frontend.components.sidebar import render_sidebar
from frontend.components.charts import create_candlestick_chart, create_score_gauge
from frontend.components.cards import metric_card, stock_card, status_badge
from frontend.components.dashboard import render_dashboard
from frontend.components.file_explorer import render_file_explorer

__all__ = [
    'render_sidebar',
    'create_candlestick_chart',
    'create_score_gauge',
    'metric_card',
    'stock_card',
    'status_badge',
    'render_dashboard',
    'render_file_explorer'
]
