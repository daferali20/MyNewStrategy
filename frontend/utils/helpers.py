# frontend/utils/helpers.py
"""
دوال مساعدة لإدارة التطبيق
"""

import streamlit as st
import pandas as pd
import os

# ============================================================================
# هيكل الملفات
# ============================================================================

FILE_STRUCTURE = {
    "📁 backend": {
        "📁 scanner": [
            "📄 __init__.py",
            "📄 breakout_scanner.py",
            "📄 screener.py",
            "📄 intraday_scanner.py",
            "📄 ai_breakout_analyzer.py"
        ],
        "📁 data_providers": [
            "📄 market_data.py"
        ],
        "📁 analysis": [
            "📄 technical.py"
        ]
    },
    "📁 frontend": {
        "📄 app.py": None,
        "📄 dashboard.py": None
    },
    "📄 requirements.txt": None,
    "📄 README.md": None
}


# ============================================================================
# دوال المساعدة
# ============================================================================

def init_session_state():
    """تهيئة متغيرات الجلسة"""
    defaults = {
        'scan_results': pd.DataFrame(),
        'selected_file': None,
        'show_file': False,
        'current_page': 'dashboard',
        'dark_mode': True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_file_content(filename):
    """جلب محتوى الملف"""
    # محاكاة - في التطبيق الحقيقي يتم قراءة الملف الفعلي
    file_contents = {
        "__init__.py": '# ملف تهيئة الوحدة\n"""وحدة المسح الضوئي"""\n\nfrom .breakout_scanner import BreakoutScanner\nfrom .screener import SmartScanner\n\n__all__ = ["BreakoutScanner", "SmartScanner"]',
        "breakout_scanner.py": '# ماسح الانفجار السعري\n\nclass BreakoutScanner:\n    def __init__(self):\n        pass\n    \n    def analyze(self, df):\n        """تحليل الانفجار"""\n        return {"score": 75, "is_breakout": True}',
        "screener.py": '# الماسح الذكي\n\nclass SmartScanner:\n    def __init__(self, symbols):\n        self.symbols = symbols\n    \n    def scan(self):\n        return []',
        "app.py": '# التطبيق الرئيسي\n\nimport streamlit as st\n\nst.title("🚀 الماسح الضوئي")\n\nif st.button("ابدأ المسح"):\n    st.success("تم المسح!")',
        "dashboard.py": '# لوحة التحكم\n\ndef show_dashboard():\n    """عرض لوحة التحكم"""\n    st.subheader("📊 لوحة التحكم")\n    st.metric("الأسهم", "150")'
    }
    
    return file_contents.get(filename, f"# محتوى الملف {filename}")


def get_sample_data():
    """الحصول على بيانات نموذجية"""
    return pd.DataFrame({
        'الرمز': ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA'],
        'الشركة': ['NVIDIA Corp', 'AMD Corp', 'Apple Inc', 'Microsoft', 'Tesla Inc'],
        'السعر': [895.32, 165.42, 175.34, 378.91, 245.68],
        'درجة الضغط': [92, 78, 85, 71, 65],
        'احتمالية الانفجار': ['85%', '72%', '68%', '55%', '48%'],
        'المخاطرة': ['منخفضة', 'متوسطة', 'منخفضة', 'متوسطة', 'مرتفعة']
    })


def format_currency(value):
    """تنسيق القيمة كعملة"""
    return f"${value:,.2f}" if value else "$0.00"
