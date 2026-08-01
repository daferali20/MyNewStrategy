# frontend/utils/state.py
"""
إدارة حالة الجلسة للتطبيق
"""

import streamlit as st
import pandas as pd

def init_session_state():
    """تهيئة جميع متغيرات الجلسة"""
    defaults = {
        'scan_results': pd.DataFrame(),
        'selected_file': None,
        'show_file': False,
        'current_page': 'dashboard',
        'selected_symbol': None,
        'analysis_results': None,
        'stock_data': None,
        'sidebar_config': None,
        'last_scan_time': None,
        'scan_in_progress': False,
        'dark_mode': True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_state(key, default=None):
    """الحصول على قيمة من حالة الجلسة"""
    return st.session_state.get(key, default)

def set_state(key, value):
    """تعيين قيمة في حالة الجلسة"""
    st.session_state[key] = value

def reset_state():
    """إعادة تعيين حالة الجلسة"""
    init_session_state()
