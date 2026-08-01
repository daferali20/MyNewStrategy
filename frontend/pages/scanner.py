# frontend/pages/scanner.py
"""
صفحة مسح السوق
تم إصلاح مشكلة الاستيراد الدائري (Circular Import) وتأمين المعاملات
"""

import streamlit as st
import pandas as pd

def render():
    """عرض صفحة المسح"""
    st.subheader("🔍 مسح السوق الآلي")
    
    # 1. قراءة الإعدادات بأمان
    config = st.session_state.get('sidebar_config', {})
    if not isinstance(config, dict):
        config = {}
    
    # 2. عرض البطاقات المباشرة
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 أدنى درجة جاهزية", f"{config.get('min_score', 70)}/100")
    with col2:
        st.metric("📊 أدنى احتمالية انفجار", f"{config.get('min_prob', 55)}%")
    with col3:
        sector = config.get('sector') or 'الكل'
        st.metric("🏢 القطاع المحدد", sector)
    
    st.markdown("---")
    
    # 3. زر التحديث (مُدار بواسطة الجلسة لمنع Circular Import)
    try:
        btn_click = st.button("🔄 بدء/تحديث المسح الآن", type="primary", key="btn_run_scanner", width="stretch")
    except TypeError:
        btn_click = st.button("🔄 بدء/تحديث المسح الآن", type="primary", key="btn_run_scanner", use_container_width=True)

    if btn_click:
        if 'sidebar_config' not in st.session_state:
            st.session_state.sidebar_config = {}
        st.session_state.sidebar_config['scan_clicked'] = True
        st.rerun()

    # 4. عرض النتائج المتوفرة في الجلسة
    results = st.session_state.get('scan_results')
    
    if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
        st.subheader(f"📊 النتائج المكتشفة ({len(results)} فرصة)")
        
        # توافقية آمنة مع Streamlit Dataframe
        try:
            st.dataframe(results, width="stretch", hide_index=True)
        except (TypeError, ValueError):
            st.dataframe(results, use_container_width=True, hide_index=True)
            
        if st.session_state.get('last_scan_time'):
            st.caption(f"🕒 تم المسح في: {st.session_state.last_scan_time}")
    else:
        if st.session_state.get('scan_in_progress', False):
            st.info("🔍 جاري تنفيذ عملية المسح حالياً، يرجى الانتظار...")
        else:
            st.info("🔍 اضغط على **'بدء/تحديث المسح الآن'** أو الزر الجانبي للبدء في اكتشاف الفرص.")
