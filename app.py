# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم
تم إصلاح مشكلة اختفاء الصفحات
"""

import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd

# ============================================================================
# إعدادات الصفحة
# ============================================================================

st.set_page_config(
    page_title="الماسح الضوئي للأسهم | Breakout Scanner",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة المسارات
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================================================
# تهيئة حالة الجلسة
# ============================================================================

def init_session_state():
    """تهيئة جميع متغيرات الجلسة"""
    defaults = {
        'scan_results': pd.DataFrame(),
        'current_page': 'dashboard',
        'sidebar_config': {},
        'last_scan_time': None,
        'scan_in_progress': False,
        'initialized': False,
        'css_loaded': False
    }
    
    if not st.session_state.get('initialized', False):
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        st.session_state.initialized = True

# ============================================================================
# استيراد المكونات - مع معالجة الأخطاء
# ============================================================================

def safe_import(module_name, fallback=None):
    """استيراد آمن مع معالجة الأخطاء"""
    try:
        return __import__(module_name, fromlist=[''])
    except ImportError as e:
        print(f"⚠️ خطأ في استيراد {module_name}: {e}")
        return fallback

# استيراد الأدوات المساعدة
try:
    from frontend.utils.helpers import load_css, get_sample_data
except ImportError:
    load_css = lambda: None
    get_sample_data = lambda: pd.DataFrame()

# استيراد الشريط الجانبي
try:
    from frontend.components.sidebar import render_sidebar
except ImportError:
    render_sidebar = lambda: {}

# استيراد الصفحات - استخدام try/except لكل صفحة
try:
    from frontend.pages.dashboard import render as render_dashboard
except ImportError:
    render_dashboard = lambda: st.warning("⚠️ صفحة لوحة التحكم غير متوفرة")

try:
    from frontend.pages.scanner import render as render_scanner
except ImportError:
    render_scanner = lambda: st.warning("⚠️ صفحة المسح غير متوفرة")

try:
    from frontend.pages.analyze import render as render_analyze
except ImportError:
    render_analyze = lambda: st.warning("⚠️ صفحة التحليل غير متوفرة")

# ============================================================================
# دوال مساعدة إضافية
# ============================================================================

def get_stock_data(symbol, period="6mo"):
    """جلب بيانات السهم - بديل في حالة عدم توفر المصادر"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

def get_sample_analysis(symbol="AAPL"):
    """تحليل نموذجي للعرض"""
    return {
        'squeeze_score': 75,
        'breakout_probability': 68,
        'expected_upside': 12.5,
        'risk_level': 'متوسط',
        'time_to_breakout': 'خلال أيام',
        'entry_points': {
            'current_price': 175.34,
            'entry_point': 178.50,
            'stop_loss': 170.00,
            'target_1': 190.00,
            'target_2': 200.00
        }
    }

# ============================================================================
# التطبيق الرئيسي
# ============================================================================

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # تهيئة حالة الجلسة
    init_session_state()
    
    # تحميل التصميم
    load_css()
    
    # عرض الهيدر
    render_header()
    
    # عرض الشريط الجانبي
    render_sidebar()
    
    # معالجة المسح
    handle_scan()
    
    # عرض الصفحة المختارة
    render_current_page()

def render_header():
    """عرض الهيدر الرئيسي"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 الماسح الضوئي للأسهم المتفجرة</h1>
        <p>اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي وتحليل الضغط (Squeeze)</p>
    </div>
    """, unsafe_allow_html=True)

def handle_scan():
    """معالجة طلب المسح"""
    config = st.session_state.get('sidebar_config', {})
    
    if config and config.get('scan_clicked', False):
        if not st.session_state.get('scan_in_progress', False):
            st.session_state.scan_in_progress = True
            
            # محاولة استخدام الماسح المتقدم
            scan_function = None
            try:
                from backend.explosive_moves.integration import ExplosiveMovesAnalyzer
                analyzer = ExplosiveMovesAnalyzer()
                scan_function = lambda s, mn, mp: analyzer.scan_multiple(
                    ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'META', 'TSLA'],
                    None
                )
            except ImportError:
                pass
            
            # استخدام الماسح الأساسي إذا لم يتوفر المتقدم
            if scan_function is None:
                try:
                    from backend.scanner.ai_breakout_analyzer import scan_market_ai
                    scan_function = scan_market_ai
                except ImportError:
                    scan_function = mock_scan
            
            with st.spinner("🔍 جاري مسح السوق..."):
                results = scan_function(
                    sector=config.get('sector'),
                    min_score=config.get('min_score', 70),
                    min_prob=config.get('min_prob', 55),
                    max_symbols=config.get('max_symbols', 15)
                )
                
                if results is not None and not results.empty:
                    st.session_state.scan_results = results
                    st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                    st.success(f"✅ تم العثور على {len(results)} فرصة!")
                else:
                    st.warning("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")
            
            st.session_state.scan_in_progress = False
            if 'sidebar_config' in st.session_state:
                st.session_state.sidebar_config['scan_clicked'] = False

def mock_scan(sector=None, min_score=60, min_prob=55, max_symbols=20):
    """دالة مسح نموذجية"""
    return get_sample_data()

def render_current_page():
    """عرض الصفحة المختارة"""
    page = st.session_state.get('current_page', 'dashboard')
    
    pages = {
        'dashboard': render_dashboard,
        'scanner': render_scanner,
        'analyze': render_analyze
    }
    
    # عرض الصفحة المختارة
    render_func = pages.get(page, render_dashboard)
    render_func()

if __name__ == "__main__":
    main()
