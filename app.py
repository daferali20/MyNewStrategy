# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم
تم إصلاح مشكلة اختفاء الصفحة وإعادة الرندر التلقائي
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
    """تهيئة جميع متغيرات الجلسة بشكل آمن وبدون تداخل"""
    if 'initialized' not in st.session_state:
        st.session_state.scan_results = pd.DataFrame()
        st.session_state.selected_file = None
        st.session_state.show_file = False
        st.session_state.current_page = 'dashboard'
        st.session_state.sidebar_config = {}
        st.session_state.last_scan_time = None
        st.session_state.scan_in_progress = False
        st.session_state.initialized = True

# ============================================================================
# استيراد المكونات والصفحات بأمان
# ============================================================================

from frontend.utils.helpers import load_css, get_sample_data
from frontend.components.sidebar import render_sidebar

try:
    from frontend.pages.dashboard import render as render_dashboard
except Exception as e:
    render_dashboard = lambda: st.warning(f"⚠️ صفحة لوحة التحكم غير متوفرة: {e}")

try:
    from frontend.pages.scanner import render as render_scanner
except Exception as e:
    render_scanner = lambda: st.warning(f"⚠️ صفحة المسح غير متوفرة: {e}")

try:
    from frontend.pages.file_explorer import render as render_file_explorer
except Exception as e:
    render_file_explorer = lambda: st.warning(f"⚠️ صفحة مستكشف الملفات غير متوفرة: {e}")

try:
    from frontend.pages.analyze import render as render_analyze
except Exception as e:
    render_analyze = lambda: st.warning(f"⚠️ صفحة التحليل غير متوفرة: {e}")

# ============================================================================
# التطبيق الرئيسي
# ============================================================================

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # 1. تهيئة حالة الجلسة
    init_session_state()
    
    # 2. تحميل التصميم
    load_css()
    
    # 3. عرض الهيدر
    render_header()
    
    # 4. عرض الشريط الجانبي (يقوم بتحديث current_page و sidebar_config في الجلسة)
    render_sidebar()
    
    # 5. معالجة طلبات المسح إذا وجدت
    handle_scan()
    
    # 6. عرض الصفحة المختارة بشكل ثابت
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
    """معالجة طلب المسح بشكل آمن ومحمي"""
    config = st.session_state.get('sidebar_config') or {}
    
    # التحقق من أن الزر تم ضغطه ولم تكن هناك عملية جارية
    if config.get('scan_clicked', False) and not st.session_state.get('scan_in_progress', False):
        st.session_state.scan_in_progress = True
        
        try:
            from backend.scanner.ai_breakout_analyzer import scan_market_ai
        except Exception as e:
            st.error(f"⚠️ فشل استيراد المحلل الآلي: {e}")
            scan_market_ai = mock_scan
        
        with st.spinner("🔍 جاري مسح السوق..."):
            try:
                results = scan_market_ai(
                    sector=config.get('sector'),
                    min_score=config.get('min_score', 70),
                    min_prob=config.get('min_prob', 55),
                    max_symbols=config.get('max_symbols', 15)
                )
                
                if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
                    st.session_state.scan_results = results
                    st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                    st.success(f"✅ تم العثور على {len(results)} فرصة!")
                else:
                    st.session_state.scan_results = pd.DataFrame()
                    st.warning("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")
            except Exception as ex:
                st.error(f"⚠️ خطأ أثناء تنفيذ الفحص: {ex}")
        
        # إنهاء حالة المسح وإطفاء الزر بأمان دون إعادة كتابة القاموس بأكمله
        st.session_state.scan_in_progress = False
        st.session_state.sidebar_config['scan_clicked'] = False

def mock_scan(sector=None, min_score=60, min_prob=55, max_symbols=20):
    """دالة مسح نموذجية لضمان عدم توقف التطبيق"""
    return get_sample_data()

def render_current_page():
    """عرض الصفحة المختارة بأسلوب ثابت لمنع الـ Flash"""
    page = st.session_state.get('current_page', 'dashboard')
    
    pages = {
        'dashboard': render_dashboard,
        'scanner': render_scanner,
        'files': render_file_explorer,
        'analyze': render_analyze
    }
    
    render_func = pages.get(page, render_dashboard)
    
    # حاوية قائمة لتثبيت الصفحة ومحاسبة الرندر
    with st.container():
        render_func()

if __name__ == "__main__":
    main()
