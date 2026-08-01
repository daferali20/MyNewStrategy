# frontend/components/file_explorer.py
"""
مكون مستكشف الملفات - عرض محتوى الملفات
"""

import streamlit as st
from frontend.utils.helpers import get_file_content

def render_file_explorer():
    """عرض مستكشف الملفات والمحتوى"""
    
    if 'selected_file' in st.session_state:
        file_name = st.session_state.selected_file
        
        st.subheader(f"📄 محتوى الملف: {file_name}")
        
        content = get_file_content(file_name)
        
        if content:
            # تحديد لغة التلوين
            ext = file_name.split('.')[-1] if '.' in file_name else 'text'
            languages = {
                'py': 'python',
                'js': 'javascript',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'md': 'markdown',
                'txt': 'text'
            }
            lang = languages.get(ext, 'text')
            st.code(content, language=lang)
        else:
            st.info(f"📝 الملف {file_name} فارغ أو غير موجود")
        
        # زر إغلاق
        if st.button("❌ إغلاق الملف"):
            st.session_state.selected_file = None
            st.session_state.show_file = False
            st.rerun()
