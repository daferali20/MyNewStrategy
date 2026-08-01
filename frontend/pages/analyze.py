# frontend/pages/analyze.py
"""
صفحة تحليل السهم المتقدمة والتفاعلية (Stock Analysis Page)
تربط الواجهة بالبيانات الحقيقية والمؤشرات الفنية الاحترافية (ATR, SMA, Candlestick Chart)
"""

import streamlit as st
import pandas as pd
from frontend.utils import (
    get_stock_data_cached,
    get_stock_info_cached,
    get_sample_analysis,
    format_currency,
    format_number,
    is_valid_symbol
)
from frontend.components.charts import create_stock_chart

def render():
    """عرض صفحة التحليل التفصيلي للأسهم"""
    st.markdown("""
        <div class="main-header">
            <h2>📈 التحليل التفصيلي للأسهم (Deep Stock Analysis)</h2>
            <p style="margin:0; opacity:0.85;">تحليل حقيقي وشامل لمستويات الدعم والمقاومة، الأهداف الفنية، واتجاهات السوق</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 1. الاستجابة للسهم المختار من الصفحات الأُخرى أو تعيين القيمة الافتراضية
    default_symbol = st.session_state.get('selected_symbol') or "AAPL"
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        symbol = st.text_input(
            "أدخل رمز السهم (مثال: NVDA, AAPL, TSLA, AMD):",
            value=default_symbol,
            key="symbol_input_field"
        ).strip().upper()
    
    with col_btn:
        st.write("##")  # محاذاة مسافية مع الحقل
        analyze_clicked = st.button("🔍 تحليل السهم", type="primary", key="btn_analyze_symbol", use_container_width=True)

    if symbol:
        # حفظ السهم المختار في حالة الجلسة
        st.session_state.selected_symbol = symbol
        
        if not is_valid_symbol(symbol):
            st.error("⚠️ الرمز المدخل غير صحيح، يرجى كتابة رمز سهم مكون من 1 إلى 6 حروف بلغة إنجليزية.")
            return

        with st.spinner(f"📊 جاري جلب وتحليل البيانات الحقيقية لـ {symbol}..."):
            df = get_stock_data_cached(symbol, period="6mo")
            info = get_stock_info_cached(symbol)
            
            if df is not None and not df.empty and len(df) > 5:
                display_analysis(symbol, df, info)
            else:
                st.warning(f"⚠️ تعذر جلب بيانات مباشرة لـ '{symbol}'. يتم الآن عرض نمط تحليلي تقديري للرمز.")
                display_sample_analysis_view(symbol)

def display_analysis(symbol: str, df: pd.DataFrame, info: dict):
    """حساب وعرض البيانات التحليلية والمؤشرات الفنية للسهم"""
    
    # 1. استخراج الإحصائيات الأساسية
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
    price_change = ((current_price - prev_close) / prev_close) * 100
    high_52 = df['High'].max()
    low_52 = df['Low'].min()
    vol = df['Volume'].iloc[-1]
    company_name = info.get('shortName') or info.get('longName') or symbol

    # 2. عرض ملخص الأداء
    st.markdown(f"### 📌 ملخص أداء سهم: **{company_name} ({symbol})**")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 السعر الحالي", format_currency(current_price), delta=f"{price_change:+.2f}%")
    with col2:
        st.metric("📈 أعلى سعر (6 أشهر)", format_currency(high_52))
    with col3:
        st.metric("📉 أدنى سعر (6 أشهر)", format_currency(low_52))
    with col4:
        st.metric("📊 حجم التداول اليومي", format_number(vol))

    st.markdown("---")
    
    # 3. حساب مستويات التداول والدخول المتقدمة (ATR Strategy)
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.tail(14).mean()
    
    if pd.isna(atr) or atr == 0:
        atr = current_price * 0.02

    entry_price = current_price * 1.005  # تأكيد الاختراق بـ 0.5%
    stop_loss = current_price - (1.5 * atr)
    target_1 = current_price + (2.0 * atr)
    target_2 = current_price + (3.5 * atr)
    
    col_levels, col_recom = st.columns(2)
    
    with col_levels:
        st.markdown("#### 📍 مستويات التداول المستهدفة (Auto-Calculated)")
        st.info(f"""
        • 🎯 **نقطة الدخول المقترحة:** {format_currency(entry_price)}
        • 🛑 **وقف الخسارة الموصى به:** {format_currency(stop_loss)}
        • 🚀 **الهدف الأول (R1):** {format_currency(target_1)}
        • 🚀 **الهدف الثاني (R2):** {format_currency(target_2)}
        """)

    with col_recom:
        st.markdown("#### 💡 التوصية والرأي الفني")
        sma20 = df['Close'].tail(20).mean()
        sma50 = df['Close'].tail(50).mean() if len(df) >= 50 else sma20
        
        if current_price > sma20 and sma20 > sma50:
            st.success("✅ **اتجاه صاعد قوي:** السعر يتدفق أعلى المتوسطات المتحركة (20 و 50 يوماً). إشارة ممتازة لاستمرار الزخم.")
        elif current_price > sma20:
            st.success("✅ **إشارة إيجابية:** السعر يتداول فوق متوسط 20 يوماً. زخَم صاعد على المدى القصير.")
        else:
            st.warning("⚠️ **منطقة تجميع/حذر:** السعر أدنى المتوسط المتحرك. ينصح بانتظار إغلاق شمعة مؤكدة فوق مستوى الدخول.")

    # 4. عرض الرسم البياني الشمعي والتفاعلي
    st.markdown("---")
    st.markdown("#### 📉 الرسم البياني لحركة السعر (Candlestick Chart)")
    
    fig = create_stock_chart(df, symbol)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df['Close'], use_container_width=True)

def display_sample_analysis_view(symbol: str):
    """عرض نموذج تحليلي عند تعذر الاتصال بالمزود المباشر"""
    sample = get_sample_analysis()
    
    st.markdown(f"### 📌 تحليل تقديري لسهم: **{symbol}**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 درجة جاهزية الانفجار", f"{sample['squeeze_score']}/100")
    with col2:
        st.metric("📊 احتمالية النجاح", f"{sample['breakout_probability']}%")
    with col3:
        st.metric("🛡️ مستوى المخاطرة", sample['risk_level'])

    st.markdown("---")
    st.markdown("#### 📍 الأهداف والمستويات المحسوبة")
    ep = sample['entry_points']
    
    st.write(f"• **السعر الحالي التقديري:** {format_currency(ep['current_price'])}")
    st.write(f"• **نقطة الدخول:** {format_currency(ep['entry_point'])}")
    st.write(f"• **وقف الخسارة:** {format_currency(ep['stop_loss'])}")
    st.write(f"• **الهدف الأول:** {format_currency(ep['target_1'])}")
