# config.py
"""
الإعدادات المركزية للتطبيق
"""

import os

# ============================================================================
# إعدادات المشروع
# ============================================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# إعدادات المسح
DEFAULT_SETTINGS = {
    'min_score': 70,
    'min_prob': 55,
    'sector': None,
    'max_symbols': 15,
    'period': '6mo'
}

# قائمة الأسهم الأمريكية
STOCK_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD',
    'INTC', 'NFLX', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'CSCO',
    'QCOM', 'TXN', 'AVGO', 'INTU', 'AMAT', 'LRCX', 'MU', 'NOW',
    'PANW', 'SNPS', 'CDNS', 'MCHP', 'ADI', 'NXPI'
]

# القطاعات المتاحة
SECTORS = ["الكل", "التكنولوجيا", "المالية", "الرعاية الصحية", "الاستهلاك", "الطاقة", "الاتصالات"]

# إعدادات التصميم
THEME = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#00E676',
    'danger': '#FF5252',
    'warning': '#FFC107',
    'info': '#29B6F6'
}

# مسارات الملفات
PATHS = {
    'css': os.path.join('frontend', 'assets', 'style.css'),
    'backend': 'backend',
    'frontend': 'frontend'
}
