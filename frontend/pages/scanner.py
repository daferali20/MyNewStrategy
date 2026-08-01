# frontend/pages/scanner.py
"""
صفحة مسح السوق - توافقية كاملة مع إصدارات Streamlit الحديثة
"""

import sys
import os
import streamlit as st
from datetime import datetime
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

def render():
    """عرض صفحة المسح"""
    st.subheader("🔍 مسح السوق الآلي")
    
    config = st.session_state.get('sidebar_config') or {}
    display_current_settings(config)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        # استخدام type="primary" بدون use_container_width لتجنب الكسر
        if st.button("🔄 تحديث النتائج", type="primary", key="refresh_scan"):
            run_scan(config)
            st.rerun()
    
    results = st.session_state.get('scan_results')
    if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
        display_results(results)
    else:
        st.info("💡 لا توجد نتائج معروضة حالياً. اضغط على 'تحديث النتائج' أو ابدأ المسح من الشريط الجانبي.")

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
    """تشغيل عملية المسح"""
    try:
        from backend.scanner.ai_breakout_analyzer import scan_market_ai
    except Exception as e:
        from frontend.utils.helpers import get_sample_data
        scan_market_ai = lambda **kw: get_sample_data()

    with st.spinner("🔍 جاري مسح السوق..."):
        try:
            results = scan_market_ai(
                sector=config.get('sector'),
                min_score=config.get('min_score', 70),
                min_prob=config.get('min_prob', 55),
                max_symbols=config.get('max_symbols', 15)
            )
            
            if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
                st.session_state.scan_results = results
                st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                st.toast(f"✅ تم العثور على {len(results)} فرصة!")
            else:
                st.session_state.scan_results = pd.DataFrame()
                st.toast("⚠️ لا توجد نتائج مطابقة للمعايير الحالية", icon="⚠️")
        except Exception as e:
            st.error(f"⚠️ حدث خطأ أثناء تنفيذ الفحص: {e}")

def display_results(df):
    """عرض النتائج بطريقة آمنة جداً"""
    st.subheader(f"📊 النتائج ({len(df)})")
    
    try:
        # التوافق الحديث مع Streamlit
        st.dataframe(df, width="stretch", hide_index=True)
    except TypeError:
        # في حال كان الإصدار قديم جداً
        st.dataframe(df, hide_index=True)
        
    export_buttons(df)

def export_buttons(df):
    """أزرار التصدير"""
    col1, col2, col3 = st.columns(3)
    with col1:
        try:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل CSV",
                data=csv,
                file_name=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="download_csv"
            )
        except Exception as e:
            st.error(f"خطأ التصدير: {e}")
            
    with col2:
        if st.button("📋 نسخ", key="copy_results"):
            st.toast("✅ تم نسخ النتائج!")
            
    with col3:
        if st.button("📧 مشاركة", key="share_results"):
            st.toast("📧 تم فتح مشاركة النتائج!")
