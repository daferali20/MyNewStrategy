# frontend/components/sidebar.py
"""
مكون الشريط الجانبي - مصحح ومحمي ضد حلقات التكرار
"""

import streamlit as st
from datetime import datetime

def render_sidebar():
    with st.sidebar:
        st.title("📍 التنقل الرئيسي")
        
        # التأكد من وجود قيمة افتراضية متطابقة
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'dashboard'

        # القائمة المربوطة بـ key='nav_radio'
        selected_page = st.radio(
            "اختر الصفحة:",
            options=['dashboard', 'scanner', 'analyze'],
            format_func=lambda x: {
                'dashboard': '📊 لوحة التحكم',
                'scanner': '🔍 المسح الضوئي',
                'analyze': '🔬 التحليل التفصيلي'
            }.get(x, x),
            key='nav_radio',
            index=['dashboard', 'scanner', 'analyze'].index(st.session_state.get('current_page', 'dashboard'))
        )

        # تحديث الجلسة في حال تم تغيير الراديو يدوياً بواسطة المستخدم
        if selected_page != st.session_state.get('current_page'):
            st.session_state['current_page'] = selected_page
            st.rerun()
def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        # 1. الشعار والعنوان
        try:
            st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        except Exception:
            pass
            
        st.title("🚀 الماسح الضوئي")
        st.markdown("---")
        
        # 2. القائمة الرئيسية (التنقل)
        render_main_menu()
        
        st.markdown("---")
        
        # 3. إعدادات المسح
        render_scan_settings()
        
        st.markdown("---")
        
        # 4. معلومات النظام
        render_system_info()
        
        return st.session_state.get('sidebar_config', {})

def render_main_menu():
    """عرض القائمة الرئيسية بشكل متوافق ومستقر"""
    pages = {
        "📊 لوحة التحكم": "dashboard",
        "🔍 مسح السوق": "scanner",
        "📈 تحليل سهم": "analyze"
    }
    
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # تحديد الفهرس الحالي لزر الراديو
    page_keys = list(pages.keys())
    page_values = list(pages.values())
    
    current_index = page_values.index(current_page) if current_page in page_values else 0
    
    selected_label = st.radio(
        "الانتقال إلى:", 
        page_keys, 
        index=current_index,
        key="main_menu_radio"
    )
    
    # تحديث الصفحة المختارة فقط إذا تغيرت عن الصفحة الحالية
    selected_page = pages[selected_label]
    if st.session_state.get('current_page') != selected_page:
        st.session_state.current_page = selected_page
        st.rerun()

def render_scan_settings():
    """عرض إعدادات المسح وتحفيز العمليات"""
    st.subheader("⚙️ إعدادات المسح")
    
    if 'sidebar_config' not in st.session_state:
        st.session_state.sidebar_config = {}
        
    config = st.session_state.sidebar_config
    
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
    current_sector = config.get('sector') or "الكل"
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
        key="max_symbols_slider"
    )
    
    # زر تشغيل المسح بتوافقية عالية للأبعاد
    try:
        scan_clicked = st.button("🔍 ابدأ المسح", type="primary", key="scan_button", width="stretch")
    except TypeError:
        scan_clicked = st.button("🔍 ابدأ المسح", type="primary", key="scan_button", use_container_width=True)
    
    # احتفاظ بالحالة السابقة لـ scan_clicked إذا لم يتم الضغط حالياً
    prev_clicked = st.session_state.sidebar_config.get('scan_clicked', False)
    
    st.session_state.sidebar_config = {
        'min_score': min_score,
        'min_prob': min_prob,
        'sector': None if sector == "الكل" else sector,
        'max_symbols': max_symbols,
        'scan_clicked': scan_clicked or prev_clicked
    }

def render_system_info():
    """عرض معلومات النظام والتوقيت"""
    if st.session_state.get('last_scan_time'):
        st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("💡 اضبط الإعدادات ثم اضغط 'ابدأ المسح'")
