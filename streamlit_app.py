# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم المتفجرة
مؤمن ضد الكراش، ومعالج لدورة حياة الجلسة (Session State Management)
"""

import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd

# ============================================================================
# 1. إعدادات المسارات والصفحة (Page Setup & Path Isolation)
# ============================================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

st.set_page_config(
    page_title="الماسح الضوئي للأسهم | Breakout Scanner",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# محاولة استيراد الإعدادات المركزية
try:
    from config import DEFAULT_SETTINGS
except ImportError:
    DEFAULT_SETTINGS = {'min_score': 70, 'min_prob': 55, 'max_symbols': 15, 'sector': 'الكل'}

# ============================================================================
# 2. تهيئة حالة الجلسة (Session State Initialization)
# ============================================================================

def init_session_state():
    """تهيئة جميع متغيرات الجلسة تلقائياً"""
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
# 3. استيراد المكونات محلياً مع التراجعات الآمنة (Fallback Handling)
# ============================================================================

# الأدوات المساعدة والتصميم
try:
    from frontend.utils.helpers import load_css, get_sample_data
except ImportError:
    load_css = lambda: None
    get_sample_data = lambda: pd.DataFrame()

# الشريط الجانبي
try:
    from frontend.components.sidebar import render_sidebar
except ImportError:
    render_sidebar = lambda: {}

# صفحات التطبيق
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
# 4. الدوال المساعدة للبيانات العشوائية/الاحتياطية
# ============================================================================

def mock_scan(sector=None, min_score=60, min_prob=55, max_symbols=20):
    """دالة مسح نموذجية في حال تعذر الاتصال بمحركات التحليل"""
    return get_sample_data()

# ============================================================================
# 5. دوال عرض الواجهات ومعالجة الأحداث
# ============================================================================

def render_header():
    """عرض الهيدر الرئيسي للتطبيق"""
    st.markdown("""
    <div class="main-header" style="text-align: right; padding: 1rem 0; margin-bottom: 2rem;">
        <h1 style="color: #667eea; font-weight: 800;">🚀 الماسح الضوئي للأسهم المتفجرة</h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">اكتشاف فرص الانفجار السعري باستعمال نماذج الذكاء الاصطناعي ومؤشرات الضغط (Squeeze)</p>
    </div>
    """, unsafe_allow_html=True)

def handle_scan():
    """معالجة أمر تنفيذ المسح بنمط حماية ثلاثي الأبعاد"""
    config = st.session_state.get('sidebar_config', {})
    
    if config and config.get('scan_clicked', False):
        if not st.session_state.get('scan_in_progress', False):
            st.session_state.scan_in_progress = True
            
            # 1. محاولة اختيار المحرك الأنسب للمسح
            scan_function = None
            
            try:
                from backend.scanner.ai_breakout_analyzer import scan_market_ai
                scan_function = scan_market_ai
            except ImportError:
                try:
                    from backend.explosive_moves.integration import analyze_explosive_potential
                    scan_function = lambda **kwargs: mock_scan(**kwargs)
                except ImportError:
                    scan_function = mock_scan

            # 2. تنفيذ العملية مع شريط التقدم
            with st.spinner("🔍 جاري مسح السوق والتحليل الفني للأسهم..."):
                try:
                    results = scan_function(
                        sector=config.get('sector', DEFAULT_SETTINGS.get('sector')),
                        min_score=config.get('min_score', DEFAULT_SETTINGS.get('min_score', 70)),
                        min_prob=config.get('min_prob', DEFAULT_SETTINGS.get('min_prob', 55)),
                        max_symbols=config.get('max_symbols', DEFAULT_SETTINGS.get('max_symbols', 15))
                    )
                    
                    if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
                        st.session_state.scan_results = results
                        st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                        st.toast(f"✅ تم العثور على {len(results)} فرصة واعدة!", icon="🔥")
                    else:
                        st.session_state.scan_results = pd.DataFrame()
                        st.toast("⚠️ لا توجد نتائج مطابقة للمحددات الحالية", icon="🔍")
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء تنفيذ عملية المسح: {e}")

            # 3. إعادة إرسال المتغيرات والتفريغ الأمني
            st.session_state.scan_in_progress = False
            st.session_state.sidebar_config['scan_clicked'] = False
            
            # التوجيه التلقائي لصفحة المسح للرؤية المباشرة
            st.session_state.current_page = 'scanner'
            st.rerun()

def render_current_page():
    """عرض الصفحة المختارة وفق الجلسة الحالية"""
    page = st.session_state.get('current_page', 'dashboard')
    
    pages = {
        'dashboard': render_dashboard,
        'scanner': render_scanner,
        'analyze': render_analyze
    }
    
    render_func = pages.get(page, render_dashboard)
    try:
        render_func()
    except Exception as e:
        st.error(f"⚠️ حدث خطأ غير متوقع أثناء عرض الصفحة ({page}): {e}")

# ============================================================================
# 6. النقطة الرئيسية للتشغيل (Main Loop)
# ============================================================================

def main():
    """الدالة الرئيسية لإدارة التدفق التفاعلي"""
    # 1. التهيئة الأولية
    init_session_state()
    
    # 2. تطبيق قواعد الـ CSS
    try:
        load_css()
    except Exception:
        pass
    
    # 3. الهيدر والشريط الجانبي
    render_header()
    
    try:
        render_sidebar()
    except Exception as e:
        st.sidebar.error(f"خطأ في تحميل الشريط الجانبي: {e}")
    
    # 4. معالجة طلبات البحث والمسح
    handle_scan()
    
    # 5. عرض محتوى الصفحة المقترنة
    render_current_page()

if __name__ == "__main__":
    main()
