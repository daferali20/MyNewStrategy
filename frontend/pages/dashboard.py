# frontend/pages/dashboard.py
"""
صفحة لوحة التحكم
"""

import streamlit as st
import pandas as pd
from frontend.utils.helpers import get_sample_data

def render():
    """عرض لوحة التحكم"""
    st.subheader("📊 نظرة عامة على السوق")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📈 الأسهم المفحوصة", "150+", delta="+12")
    with col2:
        st.metric("🔥 فرص الانفجار", "8", delta="+3")
    with col3:
        st.metric("📊 متوسط الدقة", "84.2%", delta="+2.3%")
    with col4:
        st.metric("🎯 أفضل فرصة", "NVDA", delta="+5.2%")
    
    st.markdown("---")
    
    # عرض نتائج المسح
    results = st.session_state.get('scan_results')
    if results is not None and not results.empty:
        st.subheader("📋 نتائج المسح")
        st.dataframe(results, width='stretch', hide_index=True)
    else:
        st.info("👆 اضغط 'ابدأ المسح' في الشريط الجانبي للحصول على النتائج")
