# frontend/utils/helpers.py
"""
دوال مساعدة للتطبيق - النسخة النهائية مع جميع الدوال
"""

import pandas as pd
import streamlit as st
import os
from datetime import datetime

# ============================================================================
# إعدادات المسارات
# ============================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    """تصميم مضمن في حال عدم وجود الملف"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 35px 40px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        transform: perspective(1000px) rotateX(2deg) rotateY(-2deg);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .main-header:hover {
        transform: perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1.02);
        box-shadow: 0 30px 60px -12px rgba(0,0,0,0.6), 0 0 40px rgba(102,126,234,0.3);
    }
    [data-testid="stSidebar"] {
        background: rgba(26, 26, 46, 0.92) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
        box-shadow: 10px 0 40px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        transform: perspective(800px) rotateX(0deg) rotateY(0deg);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
    }
    .metric-card:hover {
        transform: perspective(800px) rotateX(5deg) rotateY(5deg) translateY(-10px);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        border-color: rgba(102,126,234,0.3);
    }
    .metric-card .icon { font-size: 2.5rem; margin-bottom: 10px; }
    .metric-card .value { font-size: 2rem; font-weight: bold; color: white; }
    .metric-card .label { color: #888; font-size: 0.9rem; margin-top: 5px; }
    .stock-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 12px;
        border-right: 4px solid #667eea;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .stock-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(102,126,234,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# دوال التنسيق
# ============================================================================

def format_currency(value):
    """تنسيق القيمة كعملة دولار"""
    if value is None or value == 0:
        return "$0.00"
    return f"${value:,.2f}"

def format_percentage(value):
    """تنسيق النسبة المئوية"""
    if value is None:
        return "0%"
    return f"{value:.1f}%"

def format_number(value):
    """تنسيق الأرقام الكبيرة (K, M)"""
    if value is None:
        return "0"
    
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value/1_000:.2f}K"
        else:
            return f"{value:.2f}"
    except:
        return str(value)

def format_datetime(dt):
    """تنسيق التاريخ والوقت"""
    if dt is None:
        return ""
    if isinstance(dt, str):
        return dt
    return dt.strftime("%Y-%m-%d %H:%M")

def format_volume(volume):
    """تنسيق حجم التداول"""
    if volume is None or volume == 0:
        return "0"
    
    try:
        volume = float(volume)
        if volume >= 1_000_000_000:
            return f"{volume/1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"{volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume/1_000:.1f}K"
        else:
            return f"{volume:.0f}"
    except:
        return str(volume)

# ============================================================================
# دوال جلب البيانات مع التخزين المؤقت (الأسماء المطلوبة)
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_stock_data_cached(symbol, period="6mo"):
    """
    جلب بيانات السهم مع التخزين المؤقت لمدة 5 دقائق
    
    Args:
        symbol: رمز السهم (مثل AAPL)
        period: الفترة الزمنية (1mo, 3mo, 6mo, 1y, 2y)
    
    Returns:
        DataFrame ببيانات OHLCV
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return pd.DataFrame()
        
        return df
    except Exception as e:
        print(f"⚠️ خطأ في جلب بيانات {symbol}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_stock_info_cached(symbol):
    """
    جلب معلومات الشركة مع التخزين المؤقت لمدة 10 دقائق
    
    Args:
        symbol: رمز السهم
    
    Returns:
        قاموس بمعلومات الشركة
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if info else {}
    except Exception as e:
        print(f"⚠️ خطأ في جلب معلومات {symbol}: {e}")
        return {}

# أسماء بديلة للتوافق مع الإصدارات السابقة
def get_stock_data(symbol, period="6mo"):
    """اسم بديل لـ get_stock_data_cached"""
    return get_stock_data_cached(symbol, period)

def get_stock_info(symbol):
    """اسم بديل لـ get_stock_info_cached"""
    return get_stock_info_cached(symbol)

# ============================================================================
# دوال البيانات النموذجية
# ============================================================================

def get_sample_data():
    """الحصول على بيانات نموذجية للعرض"""
    return pd.DataFrame({
        'symbol': ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA'],
        'name': ['NVIDIA Corp', 'AMD Corp', 'Apple Inc', 'Microsoft', 'Tesla Inc'],
        'sector': ['التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'السيارات'],
        'current_price': [895.32, 165.42, 175.34, 378.91, 245.68],
        'squeeze_score': [92, 78, 85, 71, 65],
        'breakout_probability': [85, 72, 68, 55, 48],
        'risk_level': ['منخفض', 'متوسط', 'منخفض', 'متوسط', 'مرتفع']
    })

def get_sample_analysis():
    """الحصول على تحليل نموذجي لعرضه"""
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

def is_valid_symbol(symbol):
    """التحقق من صحة رمز السهم"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    symbol = symbol.upper().strip()
    if len(symbol) < 1 or len(symbol) > 5:
        return False
    
    return symbol.isalnum()

# ============================================================================
# دوال الملفات
# ============================================================================

def get_file_content(filename):
    """
    جلب محتوى ملف من المشروع
    
    Args:
        filename: اسم الملف
    
    Returns:
        محتوى الملف كنص
    """
    # خريطة الملفات الفعلية
    file_paths = {
        "app.py": "app.py",
        "config.py": "config.py",
        "requirements.txt": "requirements.txt",
        "README.md": "README.md",
        "breakout_scanner.py": "backend/scanner/breakout_scanner.py",
        "screener.py": "backend/scanner/screener.py",
        "ai_breakout_analyzer.py": "backend/scanner/ai_breakout_analyzer.py",
        "__init__.py": "backend/scanner/__init__.py",
        "sidebar.py": "frontend/components/sidebar.py",
        "charts.py": "frontend/components/charts.py",
        "cards.py": "frontend/components/cards.py",
        "dashboard.py": "frontend/pages/dashboard.py",
        "scanner.py": "frontend/pages/scanner.py",
        "file_explorer.py": "frontend/pages/file_explorer.py",
        "analyze.py": "frontend/pages/analyze.py",
        "helpers.py": "frontend/utils/helpers.py",
        "state.py": "frontend/utils/state.py",
        "style.css": "frontend/assets/style.css"
    }
    
    # محاولة قراءة الملف الفعلي
    if filename in file_paths:
        file_path = os.path.join(ROOT_DIR, file_paths[filename])
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
    
    # محتوى افتراضي للملفات غير الموجودة
    default_content = {
        "app.py": """# app.py - الملف الرئيسي للتطبيق
import streamlit as st

st.title("🚀 الماسح الضوئي للأسهم")
""",
        "config.py": """# config.py - الإعدادات المركزية
DEFAULT_SETTINGS = {
    'min_score': 70,
    'min_prob': 55
}
""",
        "requirements.txt": """streamlit>=1.28.0
pandas>=2.0.0
yfinance>=0.2.0
plotly>=5.14.0
""",
        "README.md": "# الماسح الضوئي للأسهم\n\nتطبيق لمسح الأسهم الأمريكية."
    }
    
    return default_content.get(filename, f"# 📝 الملف: {filename}\n\nالمحتوى غير متوفر")
