# frontend/pages/scanner.py
"""
صفحة مسح السوق الآلي (Market Scanner Page)
تم المحافظة على حل الحلقات التكرارية (Circular Import Avoidance) مع تحسين التفاعلية والتحليل السريع
"""

from datetime import datetime
import pandas as pd
import streamlit as st
from frontend.utils import (
    format_currency,
    format_percentage,
    get_sample_data,
    set_state,
)


def render():
    """عرض صفحة المسح والنتائج المباشرة"""
    st.markdown(
        """
        <div class="main-header">
            <h2>🔍 مسح السوق الآلي (Breakout & Squeeze Scanner)</h2>
            <p style="margin:0; opacity:0.85;">اكتشاف الأسهم الجاهزة للانفجار السعري بناءً على المؤشرات الفنية المتقدمة</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # 1. قراءة إعدادات الشريط الجانبي بأمان
    config = st.session_state.get('sidebar_config', {})
    if not isinstance(config, dict):
        config = {}

    # 2. عرض كروت الإحصائيات الفورية
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="🎯 أدنى درجة جاهزية (Score)",
            value=f"{config.get('min_score', 70)}/100",
        )
    with col2:
        st.metric(
            label="📊 أدنى احتمالية انفجار",
            value=f"{config.get('min_prob', 55)}%",
        )
    with col3:
        sector = config.get('sector') or 'جميع القطاعات'
        st.metric(label="🏢 القطاع المستهدف", value=sector)

    st.markdown("---")

    # 3. زر تشغيل المسح الموحد (مُدار عبر session_state لتفادي الاستيراد الدائري)
    try:
        btn_click = st.button(
            "🔄 بدء/تحديث المسح الآن",
            type="primary",
            key="btn_run_scanner",
            use_container_width=True,
        )
    except TypeError:
        btn_click = st.button(
            "🔄 بدء/تحديث المسح الآن",
            type="primary",
            key="btn_run_scanner",
        )

    if btn_click:
        if 'sidebar_config' not in st.session_state:
            st.session_state.sidebar_config = {}
        st.session_state.sidebar_config['scan_clicked'] = True
        st.session_state.scan_in_progress = True

        # في حال عدم وجود backend متصل، نعرض البيانات النموذجية لتجربة سريعة
        if st.session_state.get('scan_results') is None or st.session_state.get(
            'scan_results'
        ).empty:
            st.session_state.scan_results = get_sample_data()
            st.session_state.last_scan_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        st.rerun()

    # 4. عرض نتائج المسح
    results = st.session_state.get('scan_results')

    if (
        results is not None
        and isinstance(results, pd.DataFrame)
        and not results.empty
    ):
        st.subheader(f"⚡ الفرص المكتشفة ({len(results)} أسهم)")

        # خيار تصفية السريع للنتائج
        cols_display = [
            'symbol',
            'name',
            'sector',
            'current_price',
            'squeeze_score',
            'breakout_probability',
            'risk_level',
        ]
        available_cols = [c for c in cols_display if c in results.columns]

        df_display = results[available_cols].copy()

        # إعادة تسمية الأعمدة لتناسب الواجهة العربية
        column_mapping = {
            'symbol': 'الرمز',
            'name': 'الشركة',
            'sector': 'القطاع',
            'current_price': 'السعر الحالي ($)',
            'squeeze_score': 'درجة الجاهزية',
            'breakout_probability': 'احتمالية الانفجار (%)',
            'risk_level': 'مستوى المخاطرة',
        }
        df_display = df_display.rename(columns=column_mapping)

        # عرض الجدول بشكل أنيق وتفاعلي
        try:
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        except (TypeError, ValueError):
            st.dataframe(df_display, hide_index=True)

        if st.session_state.get('last_scan_time'):
            st.caption(
                f"🕒 آخر تحديث للمسح: {st.session_state.last_scan_time}"
            )

        st.markdown("---")
        st.subheader("🎯 تحليل سهم سريع")
        selected_stock = st.selectbox(
            "اختر سهماً للانتقال إلى التحليل التفصيلي:",
            options=results['symbol'].tolist(),
            key="scanner_stock_selector",
        )

        col_act1, col_act2 = st.columns([1, 3])
        with col_act1:
            if st.button(
                f"🔬 تحليل {selected_stock} الآن", use_container_width=True
            ):
                set_state('selected_symbol', selected_stock)
                set_state('current_page', 'analyze')
                st.rerun()

    else:
        if st.session_state.get('scan_in_progress', False):
            st.info("🔍 جاري تنفيذ عملية المسح حالياً، يرجى الانتظار...")
        else:
            st.info(
                "💡 اضغط على **'بدء/تحديث المسح الآن'** للبدء في اكتشاف الفرص المتاحة بالسوق."
            )
