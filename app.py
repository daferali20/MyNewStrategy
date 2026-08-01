# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم (Breakout Scanner)
تم إصلاح مشكلة إعادة التحميل التلقائي واختفاء الصفحة.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd

# ============================================================================
# 1. إعدادات الصفحة الأساسية
# ============================================================================

st.set_page_config(
    page_title="الماسح الضوئي للأسهم | Breakout Scanner",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة المجلد الرئيسي للمسارات لضمان الاستيراد بدون مشاكل
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================================================
# 2. تهيئة حالة الجلسة (Session State Initialization)
# ============================================================================

def init_session_state():
    """تهيئة آمنة ومستقرة لجميع متغيرات الجلسة لمنع اختفاء البيانات"""
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
# 3. استيراد الصفحات والمكونات بأمان
# ============================================================================

from frontend.utils.helpers import load_css, get_sample_data
from frontend.components.sidebar import render_sidebar

def get_page_renderers():
    """دالة جلب دوال عرض الصفحات مع معالجة الأخطاء الاستيرادية"""
    renderers = {}
    
    try:
        from frontend.pages.dashboard import render as render_dashboard
        renderers['dashboard'] = render_dashboard
    except Exception as e:
        renderers['dashboard'] = lambda: st.warning(f"⚠️ تعذر تحميل لوحة التحكم: {e}")

    try:
        from frontend.pages.scanner import render as render_scanner
        renderers['scanner'] = render_scanner
    except Exception as e:
        renderers['scanner'] = lambda: st.warning(f"⚠️ تعذر تحميل صفحة المسح: {e}")

    try:
        from frontend.pages.file_explorer import render as render_file_explorer
        renderers['files'] = render_file_explorer
    except Exception as e:
        renderers['files'] = lambda: st.warning(f"⚠️ تعذر تحميل مستكشف الملفات: {e}")

    try:
        from frontend.pages.analyze import render as render_analyze
        renderers['analyze'] = render_analyze
    except Exception as e:
        renderers['analyze'] = lambda: st.warning(f"⚠️ تعذر تحميل صفحة التحليل: {e}")

    return renderers

# ============================================================================
# 4. دوال المعالجة والواجهة
# ============================================================================

def render_header():
    """عرض الهيدر الرئيسي"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 الماسح الضوئي للأسهم المتفجرة</h1>
        <p>اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي وتحليل الضغط (Squeeze)</p>
    </div>
    """, unsafe_allow_html=True)

def handle_scan():
    """معالجة طلب الفحص بطريقة آمنة تضمن عدم تكرار الـ Rerun Loop"""
    config = st.session_state.get('sidebar_config') or {}
    
    # فحص خيار الفحص دون حظر الواجهة
    if config.get('scan_clicked', False) and not st.session_state.get('scan_in_progress', False):
        st.session_state.scan_in_progress = True
        
        try:
            from backend.scanner.ai_breakout_analyzer import scan_market_ai
        except Exception:
            scan_market_ai = mock_scan
            
        with st.spinner("🔍 جاري مسح السوق والتحليل..."):
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
                st.error(f"⚠️ حدث خطأ أثناء تنفيذ الفحص: {ex}")
        
        # إنهاء حالة المسح وإطغاء المحفز
        st.session_state.scan_in_progress = False
        if 'sidebar_config' in st.session_state and isinstance(st.session_state.sidebar_config, dict):
            st.session_state.sidebar_config['scan_clicked'] = False

def mock_scan(sector=None, min_score=60, min_prob=55, max_symbols=20):
    """دالة احتياطية في حالة عدم توفر الـ Backend"""
    return get_sample_data()

def render_current_page(page_renderers):
    """عرض الصفحة الحالية داخل حاوية محمية لمنع اختفاء المحتوى"""
    page_key = st.session_state.get('current_page', 'dashboard')
    render_func = page_renderers.get(page_key, page_renderers.get('dashboard'))
    
    # تثبيت الصفحة بـ Container لحمايتها أثناء التحديث
    with st.container():
        try:
            if render_func:
                render_func()
            else:
                st.error("⚠️ الصفحة المطلوبة غير متاحة.")
        except Exception as err:
            st.error(f"⚠️ حدث خطأ أثناء رندر الصفحة: {err}")

# ============================================================================
# 5. الدالة الرئيسية لتشغيل التطبيق
# ============================================================================

def main():
    # 1. تهيئة جلسة التطبيق
    init_session_state()
    
    # 2. تحميل ملفات CSS
    try:
        load_css()
    except Exception:
        pass
    
    # 3. رسم عناصر الهيدر والشريط الجانبي
    render_header()
    render_sidebar()
    
    # 4. معالجة عمليات البحث والفلترة
    handle_scan()
    
    # 5. جلب وتثبيت رندر الصفحات
    page_renderers = get_page_renderers()
    render_current_page(page_renderers)

if __name__ == "__main__":
    main()
