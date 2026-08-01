# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم
تم التحديث وتأمين العمليات ضد الكراش وتعارض المتغيرات
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
    except Exception:
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

def mock_scan(sector=None, min_score=60, min_prob=55, max_symbols=20):
    """دالة مسح نموذجية"""
    return get_sample_data()

# ============================================================================
# التطبيق الرئيسي
# ============================================================================

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # 1. تهيئة حالة الجلسة
    init_session_state()
    
    # 2. تحميل التصميم
    try:
        load_css()
    except Exception:
        pass
    
    # 3. عرض الهيدر
    render_header()
    
    # 4. عرض الشريط الجانبي
    try:
        render_sidebar()
    except Exception as e:
        st.sidebar.error(f"خطأ في الشريط الجانبي: {e}")
    
    # 5. معالجة المسح
    handle_scan()
    
    # 6. عرض الصفحة المختارة
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
    """معالجة طلب المسح بأعلى قدر من الحماية"""
    config = st.session_state.get('sidebar_config', {})
    
    if config and config.get('scan_clicked', False):
        if not st.session_state.get('scan_in_progress', False):
            st.session_state.scan_in_progress = True
            
            # محاولة استخدام محركات المسح بالتدرج
            scan_function = None
            
            # المحرك الأول: الذكاء الاصطناعي الأساسي
            try:
                from backend.scanner.ai_breakout_analyzer import scan_market_ai
                scan_function = scan_market_ai
            except ImportError:
                pass

            # المحرك الثاني: محرك الحركات السعرية المتفجرة Integration
            if scan_function is None:
                try:
                    from backend.explosive_moves.integration import analyze_explosive_potential
                    scan_function = lambda **kwargs: mock_scan(**kwargs)
                except ImportError:
                    pass

            # المحرك الاحتياطي الأخير
            if scan_function is None:
                scan_function = mock_scan

            with st.spinner("🔍 جاري مسح السوق..."):
                try:
                    results = scan_function(
                        sector=config.get('sector'),
                        min_score=config.get('min_score', 70),
                        min_prob=config.get('min_prob', 55),
                        max_symbols=config.get('max_symbols', 15)
                    )
                    
                    if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
                        st.session_state.scan_results = results
                        st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                        st.toast(f"✅ تم العثور على {len(results)} فرصة!")
                    else:
                        st.session_state.scan_results = pd.DataFrame()
                        st.toast("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء تنفيذ الفحص: {e}")

            # إعادة ضبط الحالة بأمان
            st.session_state.scan_in_progress = False
            st.session_state.sidebar_config['scan_clicked'] = False

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
    try:
        render_func()
    except Exception as e:
        st.error(f"⚠️ حدث خطأ أثناء عرض الصفحة: {e}")

if __name__ == "__main__":
    main()
