# frontend/utils/state.py
"""
إدارة حالة الجلسة للتطبيق (Session State Management)
النسخة المحدثة لضمان استقرار واستجابة الواجهة
"""

import streamlit as st
import pandas as pd

# القيم الافتراضية لحالة الجلسة
DEFAULT_STATE = {
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

def init_session_state():
    """تهيئة جميع متغيرات الجلسة غير الموجودة"""
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_state(key, default=None):
    """الحصول على قيمة من حالة الجلسة بأمان"""
    return st.session_state.get(key, default)

def set_state(key, value):
    """تعيين قيمة محددة في حالة الجلسة"""
    st.session_state[key] = value

def update_state(state_dict: dict):
    """تحديث أكثر من قيمة في حالة الجلسة دفعة واحدة"""
    for key, value in state_dict.items():
        st.session_state[key] = value

def reset_state():
    """إعادة تعيين كافة متغيرات الجلسة إلى قيمها الافتراضية"""
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value

def clear_state():
    """محي كامل حالة الجلسة وإعادة التهيئة من الصفر"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()
