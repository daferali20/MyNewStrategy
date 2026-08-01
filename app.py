# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم
نسخة خفيفة مع تقسيم الكود إلى ملفات متعددة
"""

import streamlit as st
import sys
import os

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
# استيراد المكونات
# ============================================================================

from config import ROOT_DIR
from frontend.utils.state import init_session_state
from frontend.components.sidebar import render_sidebar
from frontend.pages import dashboard, scanner, file_explorer, analyze
from frontend.utils.helpers import load_css

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
    
    # تشغيل المسح إذا تم الضغط على الزر
    handle_scan()
    
    # عرض الصفحة المختارة
    render_page()

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
    config = st.session_state.get('sidebar_config')
    if config and config.get('scan_clicked', False):
        if not st.session_state.get('scan_in_progress', False):
            st.session_state.scan_in_progress = True
            from backend.scanner.ai_breakout_analyzer import scan_market_ai
            import time
            from datetime import datetime
            
            with st.spinner("🔍 جاري مسح السوق..."):
                results = scan_market_ai(
                    sector=config.get('sector'),
                    min_score=config.get('min_score', 70),
                    min_prob=config.get('min_prob', 55),
                    max_symbols=config.get('max_symbols', 15)
                )
                if not results.empty:
                    st.session_state.scan_results = results
                    st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                    st.success(f"✅ تم العثور على {len(results)} فرصة!")
                else:
                    st.warning("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")
            st.session_state.scan_in_progress = False

def render_page():
    """عرض الصفحة المختارة"""
    page = st.session_state.get('current_page', 'dashboard')
    
    pages = {
        'dashboard': dashboard.render,
        'scanner': scanner.render,
        'files': file_explorer.render,
        'analyze': analyze.render
    }
    
    pages.get(page, dashboard.render)()

if __name__ == "__main__":
    main()
