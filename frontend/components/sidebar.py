# frontend/components/sidebar.py
"""
مكون الشريط الجانبي - تم إصلاح مشكلة إعادة التحميل
"""

import streamlit as st
from datetime import datetime

def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        st.title("🚀 الماسح الضوئي")
        st.markdown("---")
        
        # القائمة الرئيسية - بدون إعادة تحميل عند التغيير
        render_main_menu()
        
        st.markdown("---")
        
        # إعدادات المسح
        render_scan_settings()
        
        st.markdown("---")
        
        # معلومات النظام
        render_system_info()
        
        return st.session_state.get('sidebar_config', {})

def render_main_menu():
    """عرض القائمة الرئيسية - بدون إعادة تحميل"""
    pages = {
        "📊 لوحة التحكم": "dashboard",
        "🔍 مسح السوق": "scanner",
        "📂 مستكشف الملفات": "files",
        "📈 تحليل سهم": "analyze"
    }
    
    # استخدام session_state للحفاظ على القيمة المختارة
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # العثور على الفهرس الحالي
    current_index = 0
    for i, (key, value) in enumerate(pages.items()):
        if value == current_page:
            current_index = i
            break
    
    selected = st.radio(
        "القائمة", 
        list(pages.keys()), 
        index=current_index,
        key="main_menu_radio"
    )
    
    # تحديث الصفحة فقط إذا تغيرت
    new_page = pages[selected]
    if new_page != current_page:
        st.session_state.current_page = new_page
        # لا نستخدم st.rerun() هنا

def render_scan_settings():
    """عرض إعدادات المسح"""
    st.subheader("⚙️ إعدادات المسح")
    
    # استخدام القيم المخزنة أو الافتراضية
    config = st.session_state.get('sidebar_config', {})
    
    min_score = st.slider(
        "🎯 درجة الجاهزية", 
        50, 95, 
        config.get('min_score', 70),
        key="min_score_slider"
    )
    
    min_prob = st.slider(
        "📊 احتمالية الانفجار", 
        30, 90, 
        config.get('min_prob', 55),
        key="min_prob_slider"
    )
    
    sectors = ["الكل", "التكنولوجيا", "المالية", "الرعاية الصحية", "الاستهلاك", "الطاقة"]
    current_sector = config.get('sector') or 'الكل'
    sector_index = sectors.index(current_sector) if current_sector in sectors else 0
    
    sector = st.selectbox(
        "🏢 القطاع", 
        sectors,
        index=sector_index,
        key="sector_select"
    )
    
    max_symbols = st.slider(
        "📈 عدد الأسهم للمسح",
        5, 30, 
        config.get('max_symbols', 15),
        key="max_symbols"
    )
    
    # زر المسح - بدون إعادة تحميل
    scan_clicked = st.button(
        "🔍 ابدأ المسح", 
        width="stretch",
        type="primary",
        key="scan_button"
    )
    
    # تحديث الإعدادات في session_state
    st.session_state.sidebar_config = {
        'min_score': min_score,
        'min_prob': min_prob,
        'sector': None if sector == "الكل" else sector,
        'max_symbols': max_symbols,
        'scan_clicked': scan_clicked
    }

def render_system_info():
    """عرض معلومات النظام"""
    if st.session_state.get('last_scan_time'):
        st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
