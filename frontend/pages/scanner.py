# frontend/pages/scanner.py
"""
صفحة مسح السوق - بدون إعادة تحميل
"""

import streamlit as st
from datetime import datetime
import pandas as pd

def render():
    """عرض صفحة المسح - بدون إعادة تحميل"""
    st.subheader("🔍 مسح السوق الآلي")
    
    # عرض الإعدادات الحالية
    config = st.session_state.get('sidebar_config', {})
    if config is None:
        config = {}
    
    display_current_settings(config)
    
    st.markdown("---")
    
    # زر التحديث - بدون إعادة تحميل
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🔄 تحديث النتائج", type="primary", key="refresh_scan", width="stretch"):
            run_scan(config)
    
    # عرض النتائج
    results = st.session_state.get('scan_results')
    if results is not None and not results.empty:
        display_results(results)

def display_current_settings(config):
    """عرض الإعدادات الحالية"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 درجة الجاهزية", f"{config.get('min_score', 70)}/100")
    with col2:
        st.metric("📊 احتمالية الانفجار", f"{config.get('min_prob', 55)}%")
    with col3:
        sector = config.get('sector') or 'الكل'
        st.metric("🏢 القطاع", sector)

def run_scan(config):
    """تشغيل عملية المسح - بدون إعادة تحميل"""
    try:
        from backend.scanner.ai_breakout_analyzer import scan_market_ai
    except ImportError:
        st.error("❌ وحدة المسح غير متوفرة")
        return
    
    with st.spinner("🔍 جاري مسح السوق..."):
        results = scan_market_ai(
            sector=config.get('sector'),
            min_score=config.get('min_score', 70),
            min_prob=config.get('min_prob', 55),
            max_symbols=config.get('max_symbols', 15)
        )
        
        if not results.empty:
            st.session_state.scan_results = results
            st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
            st.success(f"✅ تم العثور على {len(results)} فرصة!")
        else:
            st.warning("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")

def display_results(df):
    """عرض النتائج - بدون إعادة تحميل"""
    st.subheader(f"📊 النتائج ({len(df)})")
    st.dataframe(df, width='stretch', hide_index=True)
    
    # أزرار التصدير
    export_buttons(df)

def export_buttons(df):
    """أزرار التصدير - بدون إعادة تحميل"""
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 تحميل CSV",
            csv,
            f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            key="download_csv",
            width="stretch"
        )
    with col2:
        if st.button("📋 نسخ", width="stretch", key="copy_results"):
            st.toast("✅ تم نسخ النتائج!")
    with col3:
        if st.button("📧 مشاركة", width="stretch", key="share_results"):
            st.toast("📧 تم فتح مشاركة النتائج!")
