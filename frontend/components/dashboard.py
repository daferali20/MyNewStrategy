# frontend/components/dashboard.py
"""
مكون لوحة التحكم
"""

import streamlit as st
import pandas as pd

def render_dashboard():
    """عرض لوحة التحكم"""
    st.subheader("📊 نظرة عامة على السوق")
    display_metrics()
    st.markdown("---")
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
    results = st.session_state.get('scan_results')
    
    if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
        df = results
        st.subheader("📋 نتائج المسح")
        
        try:
            st.dataframe(df, width="stretch", hide_index=True)
            st.caption(f"✅ تم العثور على {len(df)} فرصة مطابقة للمعايير")
        except Exception:
            st.dataframe(df, hide_index=True)
    else:
        st.info("👆 اضغط 'ابدأ المسح' في الشريط الجانبي للحصول على النتائج")
        display_sample_preview()

def display_sample_preview():
    """عرض نموذج للنتائج"""
    with st.expander("📋 نموذج للنتائج المتوقعة"):
        try:
            from frontend.utils.helpers import get_sample_data
            sample_data = get_sample_data()
            if sample_data is not None and not sample_data.empty:
                st.dataframe(sample_data, width="stretch", hide_index=True)
        except Exception as e:
            st.warning(f"⚠️ تعذر تحميل العينة: {e}")
