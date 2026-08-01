# frontend/components/dashboard.py
"""
مكون لوحة التحكم - آمن ومستقر ضد مشاكل الاختفاء والانهيار
"""

import streamlit as st
import pandas as pd

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
    """عرض نتائج المسح بأسلوب محمي من الأخطاء"""
    results = st.session_state.get('scan_results')
    
    # التحقق الآمن من وجود بيانات
    if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
        df = results
        
        st.subheader("📋 نتائج المسح")
        
        try:
            # تكوين الخصائص ديناميكياً لتجنب كسر الجدول عند غياب أي عمود
            column_config = {}
            if "symbol" in df.columns:
                column_config["symbol"] = st.column_config.TextColumn("الرمز", width="small")
            if "name" in df.columns:
                column_config["name"] = st.column_config.TextColumn("الشركة")
            if "sector" in df.columns:
                column_config["sector"] = st.column_config.TextColumn("القطاع", width="small")
            if "current_price" in df.columns:
                column_config["current_price"] = st.column_config.NumberColumn("السعر", format="$%.2f")
            if "squeeze_score" in df.columns:
                column_config["squeeze_score"] = st.column_config.ProgressColumn(
                    "درجة الضغط", 
                    format="%d/100", 
                    min_value=0, 
                    max_value=100
                )
            if "breakout_probability" in df.columns:
                column_config["breakout_probability"] = st.column_config.ProgressColumn(
                    "احتمالية الانفجار", 
                    format="%.1f%%", 
                    min_value=0, 
                    max_value=100
                )

            st.dataframe(
                df,
                column_config=column_config,
                use_container_width=True, # تم استبدال width="stretch" لمنع كسر الرندر
                hide_index=True
            )
            st.caption(f"✅ تم العثور على {len(df)} فرصة مطابقة للمعايير")
        except Exception:
            # طريقة احتياطية لعرض البيانات عند حدوث أي مشكلة في التنسيق
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("👆 اضغط 'ابدأ المسح' في الشريط الجانبي للحصول على النتائج")
        display_sample_preview()

def display_sample_preview():
    """عرض نموذج للنتائج بحماية كاملة من أخطاء الاستيراد"""
    with st.expander("📋 نموذج للنتائج المتوقعة"):
        try:
            from frontend.utils.helpers import get_sample_data
            sample_data = get_sample_data()
            if sample_data is not None and not sample_data.empty:
                st.dataframe(sample_data, use_container_width=True, hide_index=True)
            else:
                st.write("لا تتوفر بيانات نموذجية حالياً.")
        except Exception as e:
            st.warning(f"⚠️ تعذر تحميل العينة: {e}")
