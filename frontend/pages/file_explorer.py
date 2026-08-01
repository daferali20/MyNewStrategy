# frontend/pages/file_explorer.py
"""
صفحة مستكشف الملفات (File Explorer Page)
معدلة ومحصنة من أخطاء use_container_width ورموز المسارات
"""

import streamlit as st
from frontend.utils.helpers import get_file_content

def render():
    """عرض صفحة مستكشف الملفات"""
    st.markdown("""
        <div class="main-header">
            <h2>📂 مستكشف ملفات المشروع (File Explorer)</h2>
            <p style="margin:0; opacity:0.85;">تصفح وقراءة الكود المصدري وإعدادات النظام بشكل مباشر</p>
        </div>
    """, unsafe_allow_html=True)
    
    # هيكلية مجلدات وملفات المشروع
    files_tree = {
        "📁 Backend (المحرك الخلفي)": {
            "scanner": ["__init__.py", "breakout_scanner.py", "screener.py", "ai_breakout_analyzer.py"],
            "data_providers": ["market_data.py"],
            "analysis": ["technical.py"]
        },
        "📁 Frontend (الواجهة الأمامية)": {
            "": ["app.py"],
            "components": ["sidebar.py", "charts.py", "cards.py", "file_explorer.py"],
            "pages": ["dashboard.py", "scanner.py", "file_explorer.py", "analyze.py"],
            "utils": ["helpers.py", "state.py"],
            "assets": ["style.css"]
        },
        "config.py": None,
        "requirements.txt": None,
        "README.md": None
    }
    
    display_file_tree(files_tree)
    
    # عرض محتوى الملف المختار
    if st.session_state.get('show_file', False) and st.session_state.get('selected_file'):
        display_file_content()

def display_file_tree(files):
    """عرض هيكل الملفات التفاعلي"""
    for name, content in files.items():
        if isinstance(content, dict):
            with st.expander(name, expanded=False):
                for subfolder, items in content.items():
                    if subfolder:
                        st.markdown(f"**📂 {subfolder}/**")
                    for file in items:
                        display_file_item(file)
        else:
            # تنظيف اسم الملف الفردي إذا يحتوي على رموز
            clean_name = name.replace("📄 ", "").strip()
            display_file_item(clean_name)

def display_file_item(file_name):
    """عرض عنصر ملف فردي مع زر قراءة آمن"""
    clean_file_name = file_name.replace("📄 ", "").strip()
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"📄 `{clean_file_name}`")
    with col2:
        if st.button("📖 عرض", key=f"file_btn_{clean_file_name}"):
            st.session_state.selected_file = clean_file_name
            st.session_state.show_file = True
            st.rerun()

def display_file_content():
    """عرض محتوى الملف مع الدعم الآمن للتحكم"""
    file_name = st.session_state.selected_file
    st.markdown("---")
    
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.subheader(f"🔍 محتوى الملف: `{file_name}`")
    with header_col2:
        # زر إغلاق آمن متوافق مع إصدارات Streamlit الحديثة والقديمة
        try:
            close_btn = st.button("❌ إغلاق الملف", key="close_file_top", use_container_width=True)
        except TypeError:
            close_btn = st.button("❌ إغلاق الملف", key="close_file_top")
            
        if close_btn:
            st.session_state.show_file = False
            st.session_state.selected_file = None
            st.rerun()

    # قراءة المحتوى
    content = get_file_content(file_name)
    
    # تحديد لغة التظليل
    ext = file_name.split('.')[-1] if '.' in file_name else 'txt'
    lang_map = {
        'py': 'python',
        'js': 'javascript',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'md': 'markdown',
        'txt': 'text'
    }
    lang = lang_map.get(ext.lower(), 'text')
    
    st.code(content, language=lang, line_numbers=True)
    
    # زر إغلاق أسفل الصفحة للملاءمة
    try:
        if st.button("❌ إغلاق المعاينة", key="close_file_bottom", use_container_width=True):
            st.session_state.show_file = False
            st.session_state.selected_file = None
            st.rerun()
    except TypeError:
        if st.button("❌ إغلاق المعاينة", key="close_file_bottom"):
            st.session_state.show_file = False
            st.session_state.selected_file = None
            st.rerun()
