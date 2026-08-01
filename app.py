# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم
تم إصلاح جميع مشاكل None
"""

import streamlit as st
import sys
import os
from datetime import datetime

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
    """تهيئة جميع متغيرات الجلسة بشكل آمن"""
    defaults = {
        'scan_results': pd.DataFrame() if 'pd' in dir() else None,
        'selected_file': None,
        'show_file': False,
        'current_page': 'dashboard',
        'sidebar_config': {},
        'last_scan_time': None,
        'scan_in_progress': False,
        'initialized': False
    }
    
    if not st.session_state.get('initialized', False):
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        st.session_state.initialized = True

# ============================================================================
# استيراد المكونات
# ============================================================================

from frontend.utils.helpers import load_css, get_sample_data
from frontend.components.sidebar import render_sidebar

# استيراد الصفحات مع معالجة الأخطاء
try:
    from frontend.pages.dashboard import render as render_dashboard
except ImportError:
    render_dashboard = lambda: st.warning("⚠️ صفحة لوحة التحكم غير متوفرة")

try:
    from frontend.pages.scanner import render as render_scanner
except ImportError:
    render_scanner = lambda: st.warning("⚠️ صفحة المسح غير متوفرة")

try:
    from frontend.pages.file_explorer import render as render_file_explorer
except ImportError:
    render_file_explorer = lambda: st.warning("⚠️ صفحة مستكشف الملفات غير متوفرة")

try:
    from frontend.pages.analyze import render as render_analyze
except ImportError:
    render_analyze = lambda: st.warning("⚠️ صفحة التحليل غير متوفرة")

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
    """معالجة طلب المسح بشكل آمن"""
    config = st.session_state.get('sidebar_config', {})
    
    if config and config.get('scan_clicked', False):
        if not st.session_state.get('scan_in_progress', False):
            st.session_state.scan_in_progress = True
            
            try:
                from backend.scanner.ai_breakout_analyzer import scan_market_ai
            except ImportError:
                scan_market_ai = mock_scan
            
            with st.spinner("🔍 جاري مسح السوق..."):
                results = scan_market_ai(
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
            # إعادة تعيين زر المسح
            if 'sidebar_config' in st.session_state and st.session_state.sidebar_config:
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
        'files': render_file_explorer,
        'analyze': render_analyze
    }
    
    pages.get(page, render_dashboard)()

if __name__ == "__main__":
    main()
