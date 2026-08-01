# frontend/pages/dashboard.py
"""
صفحة لوحة التحكم الرئيسية
"""

import streamlit as st
import pandas as pd
from frontend.components.cards import metric_card
from frontend.utils.helpers import get_sample_data

def render():
    """عرض لوحة التحكم"""
    st.subheader("📊 نظرة عامة على السوق")
    
    # بطاقات إحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("📈", "150+", "أسهم مفحوصة")
    with col2:
        metric_card("🔥", "8", "فرص انفجار", "#FF6B6B")
    with col3:
        metric_card("📊", "84.2%", "متوسط الدقة", "#4CAF50")
    with col4:
        metric_card("🎯", "NVDA", "أفضل فرصة", "#FFD700")
    
    st.markdown("---")
    
    # عرض نتائج المسح
    if not st.session_state.get('scan_results', pd.DataFrame()).empty:
        render_scan_results()
    else:
        st.info("👆 اضغط 'ابدأ المسح' في الشريط الجانبي للحصول على النتائج")
        render_sample_preview()

def render_scan_results():
    """عرض نتائج المسح"""
    df = st.session_state.scan_results
    
    st.subheader("📋 نتائج المسح")
    st.dataframe(
        df,
        column_config={
            "symbol": st.column_config.TextColumn("الرمز", width="small"),
            "name": st.column_config.TextColumn("الشركة"),
            "sector": st.column_config.TextColumn("القطاع", width="small"),
            "current_price": st.column_config.NumberColumn("السعر", format="$%.2f"),
            "squeeze_score": st.column_config.ProgressColumn("درجة الضغط", format="%d/100", min_value=0, max_value=100),
            "breakout_probability": st.column_config.ProgressColumn("احتمالية الانفجار", format="%.1f%%", min_value=0, max_value=100)
        },
        width="stretch",
        hide_index=True
    )
    
    st.caption(f"✅ تم العثور على {len(df)} فرصة مطابقة للمعايير")

def render_sample_preview():
    """عرض نموذج للنتائج"""
    with st.expander("📋 نموذج للنتائج المتوقعة"):
        sample_data = get_sample_data()
        st.dataframe(sample_data, width="stretch", hide_index=True)
