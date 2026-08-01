# frontend/utils/helpers.py
"""
دوال مساعدة للتطبيق - النسخة المحدثة والمحصنة بالكامل
"""

import os
from datetime import datetime
import pandas as pd
import streamlit as st

# ============================================================================
# إعدادات المسارات
# ============================================================================

# تحديد المجلد الرئيسي للمشروع بدقة
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ============================================================================
# دوال التصميم (CSS)
# ============================================================================

def load_css():
    """تحميل ملف التصميم ثلاثي الأبعاد"""
    css_path = os.path.join(ROOT_DIR, "frontend", "assets", "style.css")
    
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception:
            load_inline_css()
    else:
        load_inline_css()

def load_inline_css():
    """تصميم مضمن احتياطي في حال تعذر فتح الملف"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px 35px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
    }
    [data-testid="stSidebar"] {
        background: rgba(26, 26, 46, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# دوال التنسيق المالي والعددي
# ============================================================================

def format_currency(value):
    """تنسيق القيمة كعملة دولار أمريكي"""
    if value is None or value == "":
        return "$0.00"
    try:
        val = float(value)
        return f"${val:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_percentage(value):
    """تنسيق النسبة المئوية"""
    if value is None or value == "":
        return "0.0%"
    try:
        val = float(value)
        return f"{val:.1f}%"
    except (ValueError, TypeError):
        return "0.0%"

def format_number(value):
    """تنسيق الأرقام الكبيرة (K, M, B)"""
    if value is None or value == "":
        return "0"
    
    try:
        val = float(value)
        if abs(val) >= 1_000_000_000:
            return f"{val/1_000_000_000:.2f}B"
        elif abs(val) >= 1_000_000:
            return f"{val/1_000_000:.2f}M"
        elif abs(val) >= 1_000:
            return f"{val/1_000:.2f}K"
        else:
            return f"{val:.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_datetime(dt):
    """تنسيق التاريخ والوقت"""
    if dt is None:
        return ""
    if isinstance(dt, str):
        return dt
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except AttributeError:
        return str(dt)

def format_volume(volume):
    """تنسيق حجم التداول"""
    if volume is None or volume == "":
        return "0"
    
    try:
        val = float(volume)
        if val >= 1_000_000_000:
            return f"{val/1_000_000_000:.1f}B"
        elif val >= 1_000_000:
            return f"{val/1_000_000:.1f}M"
        elif val >= 1_000:
            return f"{val/1_000:.1f}K"
        else:
            return f"{val:.0f}"
    except (ValueError, TypeError):
        return str(volume)

# ============================================================================
# دوال جلب البيانات مع التخزين المؤقت (Cached Functions)
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_data_cached(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """
    جلب بيانات السهم التاريخية مع التخزين المؤقت لمدة 5 دقائق
    """
    if not is_valid_symbol(symbol):
        return pd.DataFrame()

    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol.upper().strip())
        df = ticker.history(period=period)
        
        if df is None or df.empty:
            return pd.DataFrame()
            
        return df
    except Exception as e:
        print(f"⚠️ خطأ في جلب بيانات {symbol}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_stock_info_cached(symbol: str) -> dict:
    """
    جلب معلومات الشركة الأساسية مع التخزين المؤقت لمدة 10 دقائق
    """
    if not is_valid_symbol(symbol):
        return {}

    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol.upper().strip())
        info = ticker.info
        return info if isinstance(info, dict) else {}
    except Exception as e:
        print(f"⚠️ خطأ في جلب معلومات {symbol}: {e}")
        return {}

# أسماء بديلة للتوافق السلس مع الموديولات الأُخرى
def get_stock_data(symbol, period="6mo"):
    return get_stock_data_cached(symbol, period)

def get_stock_info(symbol):
    return get_stock_info_cached(symbol)

# ============================================================================
# دوال البيانات النموذجية والتحقق
# ============================================================================

def get_sample_data() -> pd.DataFrame:
    """الحصول على بيانات نموذجية لعرض الاختبارات"""
    return pd.DataFrame({
        'symbol': ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA'],
        'name': ['NVIDIA Corp', 'AMD Corp', 'Apple Inc', 'Microsoft', 'Tesla Inc'],
        'sector': ['التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'السيارات'],
        'current_price': [895.32, 165.42, 175.34, 378.91, 245.68],
        'squeeze_score': [92, 78, 85, 71, 65],
        'breakout_probability': [85, 72, 68, 55, 48],
        'risk_level': ['منخفض', 'متوسط', 'منخفض', 'متوسط', 'مرتفع']
    })

def get_sample_analysis() -> dict:
    """الحصول على تحليل نموذجي لعرضه عند عدم جلب بيانات"""
    return {
        'squeeze_score': 85,
        'breakout_probability': 72,
        'expected_upside': 15.5,
        'risk_level': 'منخفض',
        'time_to_breakout': 'قريباً',
        'entry_points': {
            'current_price': 895.32,
            'entry_point': 915.00,
            'stop_loss': 870.00,
            'target_1': 980.00,
            'target_2': 1050.00
        },
        'indicators': {
            'rsi': 62.5,
            'volume_ratio': 2.3,
            'bandwidth': 0.12,
            'price_position': 88.5
        }
    }

def is_valid_symbol(symbol: str) -> bool:
    """التحقق من صحة رمز السهم"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    clean_sym = symbol.upper().strip()
    if len(clean_sym) < 1 or len(clean_sym) > 6:
        return False
    
    return clean_sym.isalnum()

# ============================================================================
# دوال إدارة وقراءة الملفات
# ============================================================================

def get_file_content(filename: str) -> str:
    """
    جلب محتوى ملف نصي من المشروع بشكل آمن
    """
    file_paths = {
        "app.py": "app.py",
        "config.py": "config.py",
        "requirements.txt": "requirements.txt",
        "README.md": "README.md",
        "breakout_scanner.py": os.path.join("backend", "scanner", "breakout_scanner.py"),
        "screener.py": os.path.join("backend", "scanner", "screener.py"),
        "ai_breakout_analyzer.py": os.path.join("backend", "scanner", "ai_breakout_analyzer.py"),
        "__init__.py": os.path.join("backend", "scanner", "__init__.py"),
        "sidebar.py": os.path.join("frontend", "components", "sidebar.py"),
        "charts.py": os.path.join("frontend", "components", "charts.py"),
        "cards.py": os.path.join("frontend", "components", "cards.py"),
        "dashboard.py": os.path.join("frontend", "pages", "dashboard.py"),
        "scanner.py": os.path.join("frontend", "pages", "scanner.py"),
        "file_explorer.py": os.path.join("frontend", "pages", "file_explorer.py"),
        "analyze.py": os.path.join("frontend", "pages", "analyze.py"),
        "helpers.py": os.path.join("frontend", "utils", "helpers.py"),
        "state.py": os.path.join("frontend", "utils", "state.py"),
        "style.css": os.path.join("frontend", "assets", "style.css")
    }
    
    # 1. البحث باستخدام الخريطة المعرفة
    if filename in file_paths:
        target_path = os.path.join(ROOT_DIR, file_paths[filename])
        if os.path.exists(target_path):
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"# ⚠️ متعذر قراءة الملف {filename}: {str(e)}"
    
    # 2. البحث عن الملف داخل كامل المجلد ديناميكياً
    for root, _, files in os.walk(ROOT_DIR):
        if filename in files:
            try:
                with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"# ⚠️ متعذر قراءة الملف: {str(e)}"

    return f"# 📝 الملف ({filename}) غير موجود بمسارات المشروع."
