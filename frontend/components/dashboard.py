# frontend/components/dashboard.py
"""
مكون لوحة التحكم
"""

import streamlit as st
import pandas as pd
from frontend.utils.helpers import get_sample_data

def render_dashboard():
    """عرض لوحة التحكم"""
    st.subheader("📊 نظرة عامة على السوق")
    
    # عرض الإحصائيات
    display_metrics()
    
    st.markdown("---")
    
    # عرض نتائج المسح
    display_scan_results()

def display_metrics():
    """عرض بطاقات الإحصائيات"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">📈</div>
            <div class="value">150+</div>
            <div class="label">أسهم مفحوصة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🔥</div>
            <div class="value" style="color:#FF6B6B;">8</div>
            <div class="label">فرص انفجار</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">📊</div>
            <div class="value" style="color:#4CAF50;">84.2%</div>
            <div class="label">متوسط الدقة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🎯</div>
            <div class="value" style="color:#FFD700;">NVDA</div>
            <div class="label">أفضل فرصة</div>
        </div>
        """, unsafe_allow_html=True)

def display_scan_results():
    """عرض نتائج المسح"""
    if not st.session_state.get('scan_results', pd.DataFrame()).empty:
        df = st.session_state.scan_results
        
        st.subheader("📋 نتائج المسح")
        st.dataframe(
            df,
            column_config={
                "symbol": st.column_config.TextColumn("الرمز", width="small"),
                "name": st.column_config.TextColumn("الشركة"),
                "sector": st.column_config.TextColumn("القطاع", width="small"),
                "current_price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                "squeeze_score": st.column_config.ProgressColumn(
                    "درجة الضغط", 
                    format="%d/100", 
                    min_value=0, 
                    max_value=100
                ),
                "breakout_probability": st.column_config.ProgressColumn(
                    "احتمالية الانفجار", 
                    format="%.1f%%", 
                    min_value=0, 
                    max_value=100
                )
            },
            width="stretch",
            hide_index=True
        )
        st.caption(f"✅ تم العثور على {len(df)} فرصة مطابقة للمعايير")
    else:
        st.info("👆 اضغط 'ابدأ المسح' في الشريط الجانبي للحصول على النتائج")
        display_sample_preview()

def display_sample_preview():
    """عرض نموذج للنتائج"""
    with st.expander("📋 نموذج للنتائج المتوقعة"):
        sample_data = get_sample_data()
        st.dataframe(sample_data, width="stretch", hide_index=True)
