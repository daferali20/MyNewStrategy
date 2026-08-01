# frontend/components/dashboard.py
"""
لوحة التحكم الرئيسية - عرض الإحصائيات والنتائج
"""

import streamlit as st
import pandas as pd
from frontend.components.charts import create_candlestick_chart
from frontend.utils.helpers import get_sample_data

def render_dashboard():
    """عرض لوحة التحكم الرئيسية"""
    
    # الإحصائيات السريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 الأسهم المفحوصة", "150", delta="+12")
    with col2:
        st.metric("🔥 فرص الانفجار", "8", delta="+3")
    with col3:
        st.metric("📊 متوسط الدقة", "84.2%", delta="+2.3%")
    with col4:
        st.metric("🎯 أفضل فرصة", "NVDA", delta="+5.2%")
    
    st.markdown("---")
    
    # عرض النتائج
    if 'scan_results' in st.session_state and not st.session_state.scan_results.empty:
        render_scan_results()
    else:
        render_sample_data()


def render_scan_results():
    """عرض نتائج المسح"""
    df = st.session_state.scan_results
    
    st.subheader("📋 نتائج المسح")
    
    # عرض الجدول
    st.dataframe(
        df,
        column_config={
            "symbol": st.column_config.TextColumn("الرمز", width="small"),
            "name": st.column_config.TextColumn("الشركة"),
            "sector": st.column_config.TextColumn("القطاع"),
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
            ),
            "expected_upside": st.column_config.NumberColumn("العائد المتوقع", format="%.1f%%"),
            "risk_level": st.column_config.TextColumn("المخاطرة"),
            "time_to_breakout": st.column_config.TextColumn("توقيت الانفجار")
        },
        use_container_width=True,
        hide_index=True
    )
    
    # اختيار سهم للتحليل
    st.markdown("---")
    st.subheader("📊 تحليل مفصل")
    
    selected = st.selectbox(
        "اختر سهماً للتحليل التفصيلي:",
        df['symbol'].tolist()
    )
    
    if selected:
        render_stock_analysis(selected, df)


def render_stock_analysis(symbol, df):
    """عرض تحليل مفصل لسهم محدد"""
    
    # جلب بيانات السهم
    row = df[df['symbol'] == symbol].iloc[0]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # عرض الرسم البياني
        try:
            import yfinance as yf
            data = yf.Ticker(symbol).history(period="3mo")
            if not data.empty:
                entry_points = {
                    'entry_point': row.get('entry_point', data['Close'].iloc[-1] * 1.02),
                    'stop_loss': row.get('stop_loss', data['Close'].iloc[-1] * 0.97),
                    'target_1': row.get('target_1', data['Close'].iloc[-1] * 1.10),
                    'target_2': row.get('target_2', data['Close'].iloc[-1] * 1.20)
                }
                fig = create_candlestick_chart(data, symbol, entry_points)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"لا يمكن عرض الرسم البياني: {e}")
    
    with col2:
        st.markdown(f"### 🎯 {symbol}")
        
        # المؤشرات
        st.metric("درجة الضغط", f"{row.get('squeeze_score', 0)}/100")
        st.metric("احتمالية الانفجار", f"{row.get('breakout_probability', 0)}%")
        st.metric("العائد المتوقع", f"{row.get('expected_upside', 0)}%")
        
        st.markdown("---")
        st.markdown("#### 📍 مستويات التداول")
        st.write(f"💰 السعر: **${row.get('current_price', 0):.2f}**")
        st.write(f"📈 الدخول: **${row.get('entry_point', 0):.2f}**")
        st.write(f"🛑 وقف الخسارة: **${row.get('stop_loss', 0):.2f}**")
        st.write(f"🎯 الهدف 1: **${row.get('target_1', 0):.2f}**")
        st.write(f"🎯 الهدف 2: **${row.get('target_2', 0):.2f}**")
        
        # التوصية
        prob = row.get('breakout_probability', 0)
        if prob >= 70:
            st.success("✅ توصية: شراء قوي")
        elif prob >= 50:
            st.info("ℹ️ توصية: مراقبة")
        else:
            st.warning("⚠️ توصية: انتظار")


def render_sample_data():
    """عرض بيانات نموذجية عند عدم وجود نتائج"""
    st.info("👆 اضغط 'ابدأ المسح' في الشريط الجانبي للحصول على النتائج")
    
    st.subheader("📋 نموذج للنتائج المتوقعة")
    
    sample_data = get_sample_data()
    st.dataframe(sample_data, use_container_width=True, hide_index=True)
