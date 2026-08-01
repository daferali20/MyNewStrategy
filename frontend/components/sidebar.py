# frontend/components/sidebar.py
"""
مكون الشريط الجانبي
"""

import streamlit as st
from datetime import datetime
from config import SECTORS, DEFAULT_SETTINGS

def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        st.title("🚀 الماسح الضوئي")
        st.markdown("---")
        
        # القائمة الرئيسية
        pages = {
            "📊 لوحة التحكم": "dashboard",
            "🔍 مسح السوق": "scanner",
            "📂 مستكشف الملفات": "files",
            "📈 تحليل سهم": "analyze"
        }
        
        selected = st.radio(
            "القائمة", 
            list(pages.keys()), 
            index=0,
            key="main_menu_radio"
        )
        st.session_state.current_page = pages[selected]
        
        st.markdown("---")
        
        # إعدادات المسح
        render_scan_settings()
        
        st.markdown("---")
        
        # معلومات النظام
        render_system_info()
        
        return st.session_state.get('sidebar_config', {})

def render_scan_settings():
    """عرض إعدادات المسح"""
    st.subheader("⚙️ إعدادات المسح")
    
    min_score = st.slider(
        "🎯 درجة الجاهزية", 
        50, 95, DEFAULT_SETTINGS['min_score'],
        key="min_score_slider"
    )
    
    min_prob = st.slider(
        "📊 احتمالية الانفجار", 
        30, 90, DEFAULT_SETTINGS['min_prob'],
        key="min_prob_slider"
    )
    
    sector = st.selectbox("🏢 القطاع", SECTORS, key="sector_select")
    
    max_symbols = st.slider(
        "📈 عدد الأسهم للمسح",
        5, 30, DEFAULT_SETTINGS['max_symbols'],
        key="max_symbols"
    )
    
    scan_clicked = st.button(
        "🔍 ابدأ المسح", 
        width="stretch",
        type="primary",
        key="scan_button"
    )
    
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
    st.caption("💡 اختر صفحة من القائمة")
