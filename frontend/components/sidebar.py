# frontend/components/sidebar.py
"""
مكون الشريط الجانبي - يحتوي على القوائم والإعدادات
"""

import streamlit as st
from datetime import datetime
from frontend.utils.helpers import FILE_STRUCTURE

def render_sidebar():
    """عرض الشريط الجانبي بالكامل"""
    
    with st.sidebar:
        # الشعار
        st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        st.title("🚀 الماسح الضوئي")
        st.markdown("---")
        
        # القائمة الرئيسية
        menu_items = {
            "📊 لوحة التحكم": "dashboard",
            "🔍 مسح السوق": "scanner",
            "📂 مستكشف الملفات": "files",
            "📈 تحليل سهم": "analyze",
            "⚙️ الإعدادات": "settings"
        }
        
        selected = st.radio(
            "القائمة الرئيسية",
            options=list(menu_items.keys()),
            index=0
        )
        st.session_state['current_page'] = menu_items[selected]
        
        st.markdown("---")
        
        # عرض مستكشف الملفات إذا تم اختياره
        if st.session_state.get('current_page') == 'files':
            render_file_explorer_sidebar()
        
        st.markdown("---")
        
        # إعدادات المسح
        st.subheader("⚙️ إعدادات المسح")
        
        min_score = st.slider(
            "🎯 درجة الجاهزية",
            min_value=50,
            max_value=95,
            value=70,
            step=5,
            help="الحد الأدنى لدرجة الجاهزية"
        )
        
        min_prob = st.slider(
            "📊 احتمالية الانفجار",
            min_value=30,
            max_value=90,
            value=55,
            step=5
        )
        
        sectors = ["الكل", "التكنولوجيا", "المالية", "الرعاية الصحية", "الاستهلاك", "الطاقة"]
        selected_sector = st.selectbox("🏢 القطاع", sectors)
        
        # زر المسح
        scan_clicked = st.button(
            "🔍 ابدأ المسح",
            use_container_width=True,
            type="primary"
        )
        
        st.markdown("---")
        
        # معلومات النظام
        st.caption(f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("💡 اختر ملفاً من المستكشف")
        
        return {
            'min_score': min_score,
            'min_prob': min_prob,
            'sector': None if selected_sector == "الكل" else selected_sector,
            'scan_clicked': scan_clicked
        }


def render_file_explorer_sidebar():
    """عرض مستكشف الملفات في الشريط الجانبي"""
    st.subheader("📂 مستكشف الملفات")
    
    def display_tree(structure, indent=0):
        for key, value in structure.items():
            if isinstance(value, dict):
                expander = st.expander(f"{'  ' * indent}{key}", expanded=False)
                with expander:
                    display_tree(value, indent + 1)
            elif isinstance(value, list):
                for file in value:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"{'  ' * (indent + 1)}{file}")
                    with col2:
                        file_name = file.split('📄 ')[1] if '📄 ' in file else file
                        if st.button("📖", key=f"side_file_{file_name}"):
                            st.session_state.selected_file = file_name
                            st.session_state.show_file = True
                            st.rerun()
            else:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{'  ' * indent}{key}")
                with col2:
                    file_name = key.split('📄 ')[1] if '📄 ' in key else key
                    if st.button("📖", key=f"side_file_{file_name}"):
                        st.session_state.selected_file = file_name
                        st.session_state.show_file = True
                        st.rerun()
    
    display_tree(FILE_STRUCTURE)
