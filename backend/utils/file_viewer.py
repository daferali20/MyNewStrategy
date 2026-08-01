# backend/utils/file_viewer.py
"""
عرض محتوى الملفات - أداة مساعدة
"""

import os
import streamlit as st

class FileViewer:
    """عارض محتوى الملفات"""
    
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
    
    def get_file_tree(self, path=""):
        """الحصول على هيكل الملفات"""
        full_path = os.path.join(self.root_dir, path)
        tree = {}
        
        try:
            for item in sorted(os.listdir(full_path)):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    tree[f"📁 {item}"] = self.get_file_tree(os.path.join(path, item))
                else:
                    # إضافة معلومات الملف
                    ext = os.path.splitext(item)[1]
                    icon = self._get_file_icon(ext)
                    tree[f"{icon} {item}"] = {
                        'path': item_path,
                        'size': os.path.getsize(item_path),
                        'modified': os.path.getmtime(item_path)
                    }
        except Exception as e:
            st.error(f"خطأ في قراءة الملفات: {e}")
        
        return tree
    
    def _get_file_icon(self, ext):
        """الحصول على أيقونة حسب امتداد الملف"""
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.csv': '📊',
            '.txt': '📝',
            '.md': '📖',
            '.ipynb': '📓',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.toml': '🔧',
            '.ini': '⚙️',
            '.sh': '💻',
            '.bat': '💻',
            '.exe': '⚡'
        }
        return icons.get(ext, '📄')
    
    def read_file_content(self, file_path):
        """قراءة محتوى الملف"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"⚠️ لا يمكن قراءة الملف: {e}"
        except Exception as e:
            return f"⚠️ خطأ في قراءة الملف: {e}"


def display_file_with_syntax(content, language='python'):
    """عرض الملف مع تلوين النحو"""
    # استخدام st.code للتلوين التلقائي
    st.code(content, language=language)
