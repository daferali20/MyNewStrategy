# frontend/pages/analyze.py
"""
صفحة تحليل السهم
"""

import streamlit as st
import pandas as pd
from frontend.utils.helpers import get_stock_data_cached, get_stock_info_cached
from frontend.components.charts import create_candlestick_chart

def render():
    """عرض صفحة تحليل السهم"""
    st.subheader("📈 تحليل سهم محدد")
    
    # اختيار السهم
    symbol, period = get_user_input()
    
    if symbol:
        display_analysis(symbol, period)

def get_user_input():
    """الحصول على مدخلات المستخدم"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not st.session_state.get('scan_results', pd.DataFrame()).empty:
            symbols = st.session_state.scan_results['symbol'].tolist()
            selected = st.selectbox("اختر من النتائج:", ["-- اختر سهماً --"] + symbols, key="stock_select")
            if selected != "-- اختر سهماً --":
                symbol = selected
            else:
                symbol = st.text_input("أو أدخل رمز السهم:", value="AAPL", key="symbol_input").upper()
        else:
            symbol = st.text_input("أدخل رمز السهم (مثل: AAPL):", value="AAPL", key="symbol_input").upper()
    
    with col2:
        period = st.selectbox("الفترة:", ["1mo", "3mo", "6mo", "1y", "2y"], index=2, key="period_select")
    
    return symbol, period

def display_analysis(symbol, period):
    """عرض تحليل السهم"""
    with st.spinner(f"📊 جاري تحليل {symbol}..."):
        df = get_stock_data_cached(symbol, period=period)
        
        if df.empty:
            st.error(f"❌ لا توجد بيانات للسهم {symbol}")
            return
        
        # معلومات الشركة
        info = get_stock_info_cached(symbol)
        display_stock_info(symbol, info)
        
        # التحليل
        col1, col2 = st.columns([2, 1])
        
        with col1:
            display_chart(df, symbol)
        
        with col2:
            display_metrics(df)

def display_stock_info(symbol, info):
    """عرض معلومات الشركة"""
    company_name = info.get('longName', symbol)
    sector = info.get('sector', 'غير معروف')
    industry = info.get('industry', 'غير معروف')
    
    st.markdown(f"""
    <div class="stock-card">
        <h3>{symbol} - {company_name}</h3>
        <p>🏢 {sector} | 📊 {industry}</p>
    </div>
    """, unsafe_allow_html=True)

def display_chart(df, symbol):
    """عرض الرسم البياني"""
    current = df['Close'].iloc[-1]
    high_20 = df['High'].iloc[-20:].max()
    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or current * 0.02
    
    entry_points = {
        'entry_point': high_20 + (atr * 0.5),
        'stop_loss': current - (atr * 1.5),
        'target_1': current + (atr * 2),
        'target_2': current + (atr * 3.5)
    }
    
    fig = create_candlestick_chart(df, symbol, entry_points)
    st.plotly_chart(fig, use_container_width=True)

def display_metrics(df):
    """عرض المؤشرات والمستويات"""
    current = df['Close'].iloc[-1]
    high_20 = df['High'].iloc[-20:].max()
    low_20 = df['Low'].iloc[-20:].min()
    
    st.metric("💰 السعر الحالي", f"${current:.2f}")
    st.metric("📈 أعلى سعر (20 يوم)", f"${high_20:.2f}")
    st.metric("📉 أدنى سعر (20 يوم)", f"${low_20:.2f}")
    st.metric("📊 حجم التداول", f"{df['Volume'].iloc[-1]:,.0f}")
    
    st.markdown("---")
    display_trading_levels(df, current)

def display_trading_levels(df, current):
    """عرض مستويات التداول"""
    st.markdown("#### 📍 مستويات التداول")
    
    high_20 = df['High'].iloc[-20:].max()
    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or current * 0.02
    
    levels = [
        ('🎯 الهدف 2', high_20 + (atr * 3.5), '#AB47BC'),
        ('🎯 الهدف 1', current + (atr * 2), '#29B6F6'),
        ('📈 نقطة الدخول', high_20 + (atr * 0.5), '#00E676'),
        ('💰 السعر الحالي', current, '#FFD700'),
        ('🛑 وقف الخسارة', current - (atr * 1.5), '#FF5252')
    ]
    
    for label, value, color in sorted(levels, key=lambda x: x[1], reverse=True):
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
            <span>{label}</span>
            <span style="color:{color}; font-weight:bold;">${value:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # التوصية
    st.markdown("---")
    st.markdown("#### 💡 التوصية")
    
    if current > high_20 + (atr * 0.5):
        st.success("✅ إشارة شراء - السعر فوق نقطة الدخول")
    elif current > current - (atr * 1.5):
        st.warning("⏳ مراقبة - السعر بين الدخول ووقف الخسارة")
    else:
        st.error("❌ إشارة بيع - السعر تحت وقف الخسارة")
