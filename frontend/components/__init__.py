# frontend/components/__init__.py
"""
مكونات الواجهة - استيرادات مباشرة
"""

# استيرادات مباشرة للمكونات الأساسية
from .sidebar import render_sidebar
from .charts import create_candlestick_chart

# لا نستورد المكونات الأخرى هنا لتجنب الدائرية

__all__ = [
    'render_sidebar',
    'create_candlestick_chart'
]
