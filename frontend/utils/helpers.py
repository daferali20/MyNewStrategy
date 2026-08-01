# frontend/utils/helpers.py
"""
دوال مساعدة للتطبيق
"""

import pandas as pd
from datetime import datetime
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)
def get_stock_data_cached(symbol, period="6mo"):
    """جلب بيانات السهم مع التخزين المؤقت"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_stock_info_cached(symbol):
    """جلب معلومات الشركة مع التخزين المؤقت"""
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except:
        return {}

def format_currency(value):
    """تنسيق القيمة كعملة"""
    return f"${value:,.2f}" if value else "$0.00"

def format_number(value):
    """تنسيق الأرقام الكبيرة"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(value)

def get_file_content(filename):
    """جلب محتوى الملفات"""
    file_contents = {
        "app.py": """# الملف الرئيسي للتطبيق""",
        "breakout_scanner.py": """# ماسح الانفجار السعري""",
        "screener.py": """# الماسح الذكي""",
        "__init__.py": "# ملف تهيئة",
        "requirements.txt": "streamlit>=1.28.0\npandas>=2.0.0",
        "README.md": "# الماسح الضوئي للأسهم"
    }
    return file_contents.get(filename, f"# الملف: {filename}")

def get_sample_data():
    """الحصول على بيانات نموذجية للعرض"""
    return pd.DataFrame({
        'الرمز': ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA'],
        'الشركة': ['NVIDIA Corp', 'AMD Corp', 'Apple Inc', 'Microsoft', 'Tesla Inc'],
        'السعر': ['$895.32', '$165.42', '$175.34', '$378.91', '$245.68'],
        'درجة الضغط': ['92/100', '78/100', '85/100', '71/100', '65/100'],
        'احتمالية الانفجار': ['85%', '72%', '68%', '55%', '48%'],
        'المخاطرة': ['منخفضة', 'متوسطة', 'منخفضة', 'متوسطة', 'مرتفعة']
    })
