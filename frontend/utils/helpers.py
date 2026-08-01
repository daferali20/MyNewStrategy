# frontend/utils/helpers.py
"""
دوال مساعدة للتطبيق
تشمل: جلب البيانات، التنسيق، التصميم، والملفات
"""

import pandas as pd
import streamlit as st
import os
from datetime import datetime
import yfinance as yf

# ============================================================================
# إعدادات المسارات
# ============================================================================

# الحصول على المسار الرئيسي للمشروع
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
    /* ===== الهيدر الرئيسي ===== */
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
    .main-header h1 {
        font-size: 2.2rem;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .main-header p {
        opacity: 0.9;
        margin-top: 8px;
        font-size: 1.1rem;
    }

    /* ===== الشريط الجانبي ===== */
    [data-testid="stSidebar"] {
        background: rgba(26, 26, 46, 0.92) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
        box-shadow: 10px 0 40px rgba(0,0,0,0.3);
    }

    /* ===== بطاقات المترو ===== */
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
    .metric-card .icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: white;
    }
    .metric-card .label {
        color: #888;
        font-size: 0.9rem;
        margin-top: 5px;
    }

    /* ===== بطاقات الأسهم ===== */
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
    .stock-card h3 {
        margin: 0 0 5px 0;
        color: white;
    }
    .stock-card p {
        margin: 0;
        color: #888;
    }

    /* ===== شارات الحالة ===== */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge.buy {
        background: rgba(0,230,118,0.2);
        color: #00E676;
    }
    .status-badge.hold {
        background: rgba(255,193,7,0.2);
        color: #FFC107;
    }
    .status-badge.sell {
        background: rgba(255,82,82,0.2);
        color: #FF5252;
    }

    /* ===== شريط التمرير ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    /* ===== عناصر إضافية ===== */
    .stExpander {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stExpander:hover {
        border-color: rgba(102,126,234,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# دوال جلب البيانات
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
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if info else {}
    except Exception as e:
        print(f"⚠️ خطأ في جلب معلومات {symbol}: {e}")
        return {}

def get_multiple_stocks_data(symbols, period="6mo"):
    """
    جلب بيانات عدة أسهم دفعة واحدة
    
    Args:
        symbols: قائمة رموز الأسهم
        period: الفترة الزمنية
    
    Returns:
        قاموس {symbol: DataFrame}
    """
    result = {}
    for symbol in symbols:
        df = get_stock_data_cached(symbol, period)
        if not df.empty:
            result[symbol] = df
    return result

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

# ============================================================================
# دوال البيانات النموذجية
# ============================================================================

def get_sample_data():
    """الحصول على بيانات نموذجية للعرض"""
    return pd.DataFrame({
        'الرمز': ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA'],
        'الشركة': ['NVIDIA Corp', 'AMD Corp', 'Apple Inc', 'Microsoft', 'Tesla Inc'],
        'القطاع': ['التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'السيارات'],
        'السعر': [895.32, 165.42, 175.34, 378.91, 245.68],
        'درجة الضغط': [92, 78, 85, 71, 65],
        'احتمالية الانفجار': [85, 72, 68, 55, 48],
        'المخاطرة': ['منخفضة', 'متوسطة', 'منخفضة', 'متوسطة', 'مرتفعة']
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

# ============================================================================
# دوال إضافية
# ============================================================================

def get_stock_analysis_summary(df):
    """
    تحليل سريع لبيانات السهم واستخراج المؤشرات الأساسية
    
    Args:
        df: DataFrame ببيانات OHLCV
    
    Returns:
        قاموس بالمؤشرات
    """
    if df.empty or len(df) < 20:
        return None
    
    close = df['Close']
    volume = df['Volume']
    
    # المتوسطات المتحركة
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean() if len(close) > 50 else None
    
    # بولنجر باند
    std_20 = close.rolling(20).std()
    bb_upper = sma_20 + (std_20 * 2)
    bb_lower = sma_20 - (std_20 * 2)
    
    # آخر قيم
    current_price = close.iloc[-1]
    current_volume = volume.iloc[-1]
    avg_volume = volume.iloc[-21:-1].mean() if len(volume) > 21 else volume.mean()
    
    return {
        'current_price': current_price,
        'current_volume': current_volume,
        'avg_volume': avg_volume,
        'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1,
        'sma_20': sma_20.iloc[-1] if not sma_20.isna().iloc[-1] else None,
        'sma_50': sma_50.iloc[-1] if sma_50 is not None and not sma_50.isna().iloc[-1] else None,
        'bb_upper': bb_upper.iloc[-1],
        'bb_lower': bb_lower.iloc[-1],
        'bb_width': ((bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma_20.iloc[-1]) if sma_20.iloc[-1] > 0 else 0,
        'price_position': ((current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])) * 100
    }

def is_valid_symbol(symbol):
    """التحقق من صحة رمز السهم"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    symbol = symbol.upper().strip()
    if len(symbol) < 1 or len(symbol) > 5:
        return False
    
    # التحقق من أنه يتكون من حروف وأرقام فقط
    return symbol.isalnum()

# ============================================================================
# تصدير الدوال للاستخدام في ملفات أخرى
# ============================================================================

__all__ = [
    # التصميم
    'load_css',
    'load_inline_css',
    
    # البيانات
    'get_stock_data_cached',
    'get_stock_info_cached',
    'get_multiple_stocks_data',
    
    # التنسيق
    'format_currency',
    'format_percentage',
    'format_number',
    'format_datetime',
    'format_volume',
    
    # الملفات
    'get_file_content',
    
    # البيانات النموذجية
    'get_sample_data',
    'get_sample_analysis',
    
    # تحليل إضافي
    'get_stock_analysis_summary',
    'is_valid_symbol'
]
