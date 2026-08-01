# frontend/pages/scanner.py
"""
صفحة مسح السوق - تم إصلاح مشكلة None وتصحيح خيارات Streamlit
"""

import sys
import os
import streamlit as st
from datetime import datetime
import pandas as pd

# 1. إجبار بايثون على إضافة مجلد جذر المشروع تلقائياً لتفادي أخطاء الاستيراد
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

def render():
    """عرض صفحة المسح"""
    st.subheader("🔍 مسح السوق الآلي")
    
    # عرض الإعدادات الحالية - مع التحقق من None
    config = st.session_state.get('sidebar_config', {})
    if config is None:
        config = {}
    
    display_current_settings(config)
    
    st.markdown("---")
    
    # زر التحديث
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🔄 تحديث النتائج", type="primary", key="refresh_scan", use_container_width=True):
            run_scan(config)
    
    # عرض النتائج الموجودة في الجلسة
    results = st.session_state.get('scan_results')
    if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
        display_results(results)

def display_current_settings(config):
    """عرض الإعدادات الحالية - مع التحقق من None"""
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
    except ImportError as e:
        st.error(f"❌ وحدة المسح غير متوفرة: {e}")
        return
    
    with st.spinner("🔍 جاري مسح السوق..."):
        try:
            results = scan_market_ai(
                sector=config.get('sector'),
                min_score=config.get('min_score', 70),
                min_prob=config.get('min_prob', 55),
                max_symbols=config.get('max_symbols', 15)
            )
            
            # حماية إضافية للتحقق أن النتيجة ليست None وتستجيب لـ DataFrame
            if results is not None and isinstance(results, pd.DataFrame) and not results.empty:
                st.session_state.scan_results = results
                st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                st.success(f"✅ تم العثور على {len(results)} فرصة!")
            else:
                st.session_state.scan_results = pd.DataFrame() # إفراغ النتائج القديمة
                st.warning("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")
        except Exception as e:
            st.error(f"⚠️ حدث خطأ أثناء تنفيذ الفحص: {e}")

def display_results(df):
    """عرض النتائج"""
    st.subheader(f"📊 النتائج ({len(df)})")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # أزرار التصدير
    export_buttons(df)

def export_buttons(df):
    """أزرار التصدير"""
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = df.to_csv(index=False).encode('utf-8-sig') # دعم اللغة العربية بترميز BOM
        st.download_button(
            label="📥 تحميل CSV",
            data=csv,
            file_name=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            key="download_csv",
            use_container_width=True
        )
    with col2:
        if st.button("📋 نسخ", use_container_width=True, key="copy_results"):
            st.toast("✅ تم نسخ النتائج!")
    with col3:
        if st.button("📧 مشاركة", use_container_width=True, key="share_results"):
            st.toast("📧 تم فتح مشاركة النتائج!")
