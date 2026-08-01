# frontend/pages/scanner.py
"""
صفحة مسح السوق
"""

import streamlit as st
from datetime import datetime
import pandas as pd

def render():
    """عرض صفحة المسح"""
    st.subheader("🔍 مسح السوق الآلي")
    
    config = st.session_state.get('sidebar_config', {})
    if config is None:
        config = {}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 درجة الجاهزية", f"{config.get('min_score', 70)}/100")
    with col2:
        st.metric("📊 احتمالية الانفجار", f"{config.get('min_prob', 55)}%")
    with col3:
        sector = config.get('sector') or 'الكل'
        st.metric("🏢 القطاع", sector)
    
    st.markdown("---")
    
    # زر التحديث
    if st.button("🔄 تحديث النتائج", type="primary", key="refresh_scan", width="stretch"):
        from app import handle_scan
        handle_scan()
    
    # عرض النتائج
    results = st.session_state.get('scan_results')
    if results is not None and not results.empty:
        st.subheader(f"📊 النتائج ({len(results)})")
        st.dataframe(results, width='stretch', hide_index=True)
    else:
        st.info("🔍 اضغط 'تحديث النتائج' لبدء المسح")
