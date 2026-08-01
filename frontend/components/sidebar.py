# frontend/components/sidebar.py
"""
مكون الشريط الجانبي (Sidebar Component)
يدير أدوات التنقل بين الصفحات وإعدادات معايير المسح الضوئي.
"""

import streamlit as st

# استيراد الإعدادات الافتراضية بأمان
try:
    from config import DEFAULT_SETTINGS
except ImportError:
    DEFAULT_SETTINGS = {
        'min_score': 70,
        'min_prob': 55,
        'max_symbols': 15,
        'sector': 'الكل'
    }

def render_sidebar():
    """
    رسم وتصميم الشريط الجانبي وإدارة خيارات المسح والتنقل.
    
    :return: dict يحتوي على إعدادات المسح الحالية ونقر زر المسح.
    """
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <h2 style="margin:0; color:#667eea;">📊 خيارات التحكم</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # ====================================================================
        # 1. قائمة التنقل بين الصفحات (Navigation Menu)
        # ====================================================================
        st.subheader("📍 التنقل الرئيسي")
        
        # التأكد من وجود قيمة افتراضية للصفحة الحالية
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'dashboard'
            
        pages_map = {
            'dashboard': '📊 لوحة التحكم',
            'scanner': '🔍 المسح الضوئي',
            'analyze': '🔬 التحليل التفصيلي'
        }
        
        pages_keys = list(pages_map.keys())
        current_page = st.session_state.get('current_page', 'dashboard')
        
        # تحديد الفهرس الحالي بأمان
        default_index = pages_keys.index(current_page) if current_page in pages_keys else 0

        # خيار التنقل عبر Radio Button - استخدام key فريد
        selected_page = st.radio(
            "اختر الصفحة:",
            options=pages_keys,
            format_func=lambda x: pages_map.get(x, x),
            index=default_index,
            key='sidebar_nav_radio'  # تم تغيير المفتاح لمنع التعارض
        )

        # تحديث الصفحة الحالية (بدون st.rerun() لتجنب إعادة التحميل المتكررة)
        if selected_page != st.session_state.get('current_page'):
            st.session_state['current_page'] = selected_page

        st.markdown("---")

        # ====================================================================
        # 2. إعدادات ومعايير البحث/المسح (Scan Settings)
        # ====================================================================
        st.subheader("⚙️ إعدادات المسح")

        # اختيار القطاع
        sectors = ['الكل', 'التكنولوجيا', 'الرعاية الصحية', 'الخدمات المالية', 'الطاقة', 'الصناعة']
        
        # الحصول على القطاع المخزن أو استخدام الافتراضي
        saved_sector = st.session_state.get('sidebar_sector', DEFAULT_SETTINGS.get('sector', 'الكل'))
        sector_index = sectors.index(saved_sector) if saved_sector in sectors else 0
        
        selected_sector = st.selectbox(
            "القطاع المستهدف:",
            options=sectors,
            index=sector_index,
            key='sidebar_sector'
        )

        # الحد الأدنى لدرجة الضغط (Squeeze Score)
        min_score = st.slider(
            "الحد الأدنى لدرجة الجاهزية (Score):",
            min_value=50,
            max_value=95,
            value=int(DEFAULT_SETTINGS.get('min_score', 70)),
            step=5,
            key='sidebar_min_score'
        )

        # الحد الأدنى للاحتمالية (Probability)
        min_prob = st.slider(
            "الحد الأدنى للاحتمالية (%):",
            min_value=40,
            max_value=90,
            value=int(DEFAULT_SETTINGS.get('min_prob', 55)),
            step=5,
            key='sidebar_min_prob'
        )

        # عدد الأسهم المستهدفة
        max_symbols = st.number_input(
            "أقصى عدد للأسهم:",
            min_value=5,
            max_value=50,
            value=int(DEFAULT_SETTINGS.get('max_symbols', 15)),
            step=5,
            key='sidebar_max_symbols'
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ====================================================================
        # 3. زر بدء المسح الضوئي (Scan Trigger Button)
        # ====================================================================
        scan_clicked = st.button(
            "🚀 بدء المسح الضوئي الان",
            type="primary",
            width="stretch",  # تم التحديث: use_container_width → width
            key='btn_start_scan_sidebar'
        )

        # معالجة النقر على الزر - بدون st.rerun()
        if scan_clicked:
            # توجيه تلقائي لصفحة المسح الضوئي
            st.session_state['current_page'] = 'scanner'

        # تجميع وحفظ الإعدادات في الجلسة
        config = {
            'sector': None if selected_sector == "الكل" else selected_sector,
            'min_score': int(min_score),
            'min_prob': int(min_prob),
            'max_symbols': int(max_symbols),
            'scan_clicked': scan_clicked
        }
        
        st.session_state['sidebar_config'] = config

        # معلومات سريعة عن الجلسة
        st.markdown("---")
        if st.session_state.get('last_scan_time'):
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
        st.caption(f"🕐 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")

        return config
