# frontend/pages/analyze.py
"""
صفحة تحليل السهم المحسنّة والتفاعلية
تربط الواجهة ببيانات السوق الحقيقية وتستخرج مستويات الدعم والمقاومة والأهداف ديناميكياً
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render():
    """عرض صفحة تحليل السهم"""
    st.subheader("📈 تحليل سهم محدد")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        symbol = st.text_input(
            "أدخل رمز السهم (مثل: AAPL, NVDA, TSLA):",
            value="AAPL",
            key="symbol_input"
        ).strip().upper()
    
    with col_btn:
        st.write("##") # محاذاة مسافية
        analyze_clicked = st.button("🔍 تحليل السهم", type="primary", key="btn_analyze_symbol")

    if symbol:
        with st.spinner(f"📊 جاري تحليل البيانات الحقيقية لـ {symbol}..."):
            # جلب البيانات عبر الدالة المساعدة المحصنة
            df = fetch_stock_history(symbol)
            
            if df is not None and not df.empty and len(df) > 5:
                display_analysis(symbol, df)
            else:
                st.warning(f"⚠️ تعذر جلب بيانات صحيحة للرمز '{symbol}'. يرجى التأكد من رمز السهم والاتصال بالإنترنت.")

def fetch_stock_history(symbol: str) -> pd.DataFrame:
    """جلب بيانات السهم من yfinance بشكل آمن"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")
        return df
    except Exception as e:
        # حل احتياطي إذا تعثر الاتصال
        return pd.DataFrame()

def display_analysis(symbol: str, df: pd.DataFrame):
    """حساب وعرض المعطيات التحليلية لسهم محدد بناءً على بياناته الحقيقية"""
    
    # 1. استخراج المؤشرات الأساسية
    current_price = df['Close'].iloc[-1]
    high_52 = df['High'].max()
    low_52 = df['Low'].min()
    prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
    price_change = ((current_price - prev_close) / prev_close) * 100
    
    # 2. عرض المتركس الحقيقية
    st.markdown(f"### 📌 ملخص أداء السهم ({symbol})")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 السعر الحالي", f"${current_price:.2f}", delta=f"{price_change:+.2f}%")
    with col2:
        st.metric("📈 أعلى سعر (المناطق العلوية)", f"${high_52:.2f}")
    with col3:
        st.metric("📉 أدنى سعر (المناطق السفلى)", f"${low_52:.2f}")
    with col4:
        vol = df['Volume'].iloc[-1]
        st.metric("📊 حجم تداول اليوم", f"{vol:,.0f}")

    st.markdown("---")
    
    # 3. حساب مستويات التداول والدخول المتوقعة ديناميكياً
    atr = (df['High'] - df['Low']).tail(14).mean() # متوسط النطاق الحقيقي للتقلب
    entry_price = current_price * 1.01  # اختراق المقاومة الفورية بـ 1%
    stop_loss = current_price - (1.5 * atr)
    target_1 = current_price + (2.0 * atr)
    target_2 = current_price + (3.5 * atr)
    
    col_levels, col_recom = st.columns(2)
    
    with col_levels:
        st.markdown("#### 📍 مستويات التداول المستهدفة (Auto-Calculated)")
        st.write(f"📈 نقطة الدخول المقترحة: **${entry_price:.2f}**")
        st.write(f"🛑 وقف الخسارة الحاسم: **${stop_loss:.2f}**")
        st.write(f"🎯 الهدف الأول (R1): **${target_1:.2f}**")
        st.write(f"🎯 الهدف الثاني (R2): **${target_2:.2f}**")

    with col_recom:
        st.markdown("#### 💡 التوصية الفنية المبدئية")
        sma20 = df['Close'].tail(20).mean()
        
        if current_price > sma20:
            st.success("✅ **إشارة إيجابية:** السعر يتدفق فوق المتوسط المتحرك 20 يوماً (اتجاه صاعد فرعي).")
        else:
            st.warning("⚠️ **إشارة تجميع/حذر:** السعر تحت المتوسط 20 يوماً، يفضل انتظار الاختراق.")

    # 4. عرض رسم بياني سريع ومبسط للأسعار
    st.markdown("---")
    st.markdown("#### 📉 مسار حركة السعر (آخر 6 أشهر)")
    st.line_chart(df['Close'])
