# frontend/components/__init__.py
"""
مكونات الواجهة القابلة لإعادة الاستخدام
"""

# استيرادات بسيطة فقط
from .sidebar import render_sidebar
from .charts import create_candlestick_chart, create_score_gauge
from .cards import metric_card, stock_card, status_badge

# لا نستورد dashboard هنا لتجنب الدائرية
# سيتم استيراده عند الحاجة في app.py

__all__ = [
    'render_sidebar',
    'create_candlestick_chart',
    'create_score_gauge',
    'metric_card',
    'stock_card',
    'status_badge'
]
