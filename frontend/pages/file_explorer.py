# frontend/pages/file_explorer.py
"""
صفحة مستكشف الملفات
"""

import streamlit as st
from frontend.utils.helpers import get_file_content

def render():
    """عرض مستكشف الملفات"""
    st.subheader("📂 مستكشف الملفات")
    
    # هيكل الملفات
    files = {
        "📁 Backend": {
            "scanner": ["__init__.py", "breakout_scanner.py", "screener.py", "ai_breakout_analyzer.py"],
            "data_providers": ["market_data.py"],
            "analysis": ["technical.py"]
        },
        "📁 Frontend": {
            "": ["app.py"],
            "components": ["sidebar.py", "charts.py", "cards.py", "file_explorer.py"],
            "pages": ["dashboard.py", "scanner.py", "file_explorer.py", "analyze.py"],
            "utils": ["helpers.py", "state.py"],
            "assets": ["style.css"]
        },
        "📄 config.py": None,
        "📄 requirements.txt": None,
        "📄 README.md": None
    }
    
    display_file_tree(files)
    
    # عرض محتوى الملف المختار
    if st.session_state.get('show_file', False):
        display_file_content()

def display_file_tree(files):
    """عرض هيكل الملفات"""
    for name, content in files.items():
        if isinstance(content, dict):
            with st.expander(name, expanded=False):
                for subfolder, items in content.items():
                    if subfolder:
                        st.markdown(f"**📂 {subfolder}/**")
                    for file in items:
                        display_file_item(file)
        else:
            display_file_item(name)

def display_file_item(file):
    """عرض عنصر ملف فردي"""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"   📄 {file}")
    with col2:
        if st.button("📖", key=f"file_btn_{file}"):
            st.session_state.selected_file = file
            st.session_state.show_file = True
            st.rerun()

def display_file_content():
    """عرض محتوى الملف"""
    file_name = st.session_state.selected_file
    st.markdown("---")
    st.subheader(f"📄 محتوى: {file_name}")
    
    content = get_file_content(file_name)
    ext = file_name.split('.')[-1] if '.' in file_name else 'txt'
    lang_map = {'py': 'python', 'js': 'javascript', 'html': 'html', 'css': 'css', 'json': 'json', 'md': 'markdown'}
    lang = lang_map.get(ext, 'text')
    
    st.code(content, language=lang)
    
    if st.button("❌ إغلاق", key="close_file", width="stretch"):
        st.session_state.show_file = False
        st.session_state.selected_file = None
        st.rerun()
