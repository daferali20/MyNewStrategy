# frontend/components/file_explorer.py
"""
مكون مستكشف الملفات (File Explorer)
مُصلح ومحدث ليشمل حزمة explosive_moves ويمنع تكرار مفاتيح Streamlit
"""

import streamlit as st
import os

try:
    from frontend.utils.helpers import get_file_content
except ImportError:
    def get_file_content(path):
        return f"# تعذر قراءة الملف: {path}"

def render():
    """الدالة الرئيسية لعرض المستكشف"""
    render_file_explorer()

def render_file_explorer():
    """عرض مستكشف الملفات"""
    st.subheader("📂 مستكشف هياكل ملفات النظام")
    
    # هيكل المشروع كاملاً بعد التحديثات
    files_tree = {
        "📁 Backend": {
            "scanner": ["backend/scanner/__init__.py", "backend/scanner/breakout_scanner.py", "backend/scanner/screener.py", "backend/scanner/ai_breakout_analyzer.py"],
            "explosive_moves": [
                "backend/explosive_moves/__init__.py", "backend/explosive_moves/squeeze_detector.py", 
                "backend/explosive_moves/volatility.py", "backend/explosive_moves/smart_money.py", 
                "backend/explosive_moves/integration.py", "backend/explosive_moves/score.py"
            ],
            "data_providers": ["backend/data_loader.py"]
        },
        "📁 Frontend": {
            "root": ["app.py", "config.py"],
            "components": ["frontend/components/sidebar.py", "frontend/components/dashboard.py", "frontend/components/file_explorer.py"],
            "pages": ["frontend/pages/dashboard.py", "frontend/pages/scanner.py", "frontend/pages/analyze.py"],
            "utils": ["frontend/utils/helpers.py"]
        },
        "📄 Config & System": ["requirements.txt", "README.md"]
    }
    
    display_file_tree(files_tree)
    
    # عرض محتوى الملف المختار
    if st.session_state.get('show_file', False):
        display_file_content()

def display_file_tree(tree):
    """عرض هيكل الشجرة"""
    for category, content in tree.items():
        if isinstance(content, dict):
            with st.expander(category, expanded=False):
                for subfolder, items in content.items():
                    if subfolder and subfolder != "root":
                        st.markdown(f"**📂 {subfolder}/**")
                    for file_path in items:
                        display_file_item(file_path)
        elif isinstance(content, list):
            with st.expander(category, expanded=False):
                for file_path in content:
                    display_file_item(file_path)

def display_file_item(file_path: str):
    """عرض عنصر ملف فردي وتعيين مفتاح فريد لمنع الاستدعاء المزدوج"""
    file_display_name = os.path.basename(file_path)
    # توليد مفتاح فريد يعتمد على المسار الكامل للحد من التضارب
    unique_key = f"btn_view_{file_path.replace('/', '_').replace('.', '_')}"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"📄 `{file_display_name}`")
    with col2:
        if st.button("📖", key=unique_key, help=f"عرض محتوى {file_path}"):
            st.session_state.selected_file_path = file_path
            st.session_state.show_file = True
            st.rerun()

def display_file_content():
    """عرض محتوى الملف المحدد"""
    file_path = st.session_state.get('selected_file_path', '')
    if not file_path:
        return

    st.markdown("---")
    st.subheader(f"📄 محتوى الملف: `{file_path}`")
    
    content = get_file_content(file_path)
    
    ext = file_path.split('.')[-1] if '.' in file_path else 'txt'
    lang_map = {
        'py': 'python', 
        'js': 'javascript', 
        'html': 'html', 
        'css': 'css', 
        'json': 'json', 
        'md': 'markdown'
    }
    lang = lang_map.get(ext, 'text')
    
    st.code(content, language=lang)
    
    # زر الإغلاق المتوافق
    try:
        close_btn = st.button("❌ إغلاق المحرر", key="close_file_viewer", width="stretch")
    except TypeError:
        close_btn = st.button("❌ إغلاق المحرر", key="close_file_viewer", use_container_width=True)

    if close_btn:
        st.session_state.show_file = False
        st.session_state.selected_file_path = None
        st.rerun()
