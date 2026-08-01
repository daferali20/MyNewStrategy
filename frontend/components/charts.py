# frontend/components/charts.py
"""
مكونات الرسوم البيانية المتطورة لصفحات التحليل الفني
مُصلح ومُحصّن لجميع حالات التداول وتخطيطات العرض
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_candlestick_chart(df: pd.DataFrame, symbol: str, entry_points: dict = None):
    """
    إنشاء رسم بياني تفاعلي للشموع اليابانية مع الأحجام والمتوسطات المتحركة
    """
    # 1. فحص حماية البيانات
    if df is None or df.empty or not all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        fig = go.Figure()
        fig.update_layout(
            title=f"⚠️ لا تتوفر بيانات رسم بياني لكود السهم: {symbol}",
            template="plotly_dark",
            height=400
        )
        return fig

    # 2. إنشاء رسم بياني مزدوج (الأسعار فوق وحجم التداول تحت)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.8, 0.2]
    )

    # 3. رسم الشموع اليابانية
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="السعر",
        increasing=dict(line=dict(color='#00E676')),
        decreasing=dict(line=dict(color='#FF5252'))
    ), row=1, col=1)

    # 4. إضافة المتوسطات المتحركة SMA20 & SMA50
    if len(df) >= 20:
        ma20 = df['Close'].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma20,
            line=dict(color='#FFD700', width=1.2),
            name="MA20",
            opacity=0.8
        ), row=1, col=1)

    if len(df) >= 50:
        ma50 = df['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma50,
            line=dict(color='#29B6F6', width=1.2),
            name="MA50",
            opacity=0.8
        ), row=1, col=1)

    # 5. إضافة حجم التداول (Volume) إن وجد
    if 'Volume' in df.columns:
        colors = ['#00E676' if row['Close'] >= row['Open'] else '#FF5252' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name="حجم التداول",
            marker_color=colors,
            opacity=0.6
        ), row=2, col=1)

    # 6. إضافة مستويات الدخول والأهداف ووقف الخسارة
    if entry_points and isinstance(entry_points, dict):
        add_levels(fig, entry_points)

    # 7. تحسين المظهر الخارجي والعرض
    fig.update_layout(
        title=f"📈 التحليل الفني لـ ({symbol})",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=520,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    # إزالة عطلات نهاية الأسبوع من محور الوقت لتجنب الفجوات
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    
    return fig

def add_levels(fig, entry_points: dict):
    """إضافة خطوط مستويات التداول المستهدفة"""
    levels = [
        ('entry_point', '#00E676', 'نقطة الدخول', 'top right'),
        ('stop_loss', '#FF5252', 'وقف الخسارة', 'bottom right'),
        ('target_1', '#29B6F6', 'الهدف 1', 'top left'),
        ('target_2', '#AB47BC', 'الهدف 2', 'bottom left')
    ]
    for key, color, label, position in levels:
        if key in entry_points and entry_points[key] is not None:
            fig.add_hline(
                y=entry_points[key],
                line_dash="dash",
                line_color=color,
                annotation_text=f"{label}: ${entry_points[key]:.2f}",
                annotation_position=position,
                row=1, col=1
            )

def create_score_gauge(score: float, title: str = "الدرجة"):
    """إنشاء مقياس دائري عالي الجودة للنتائج والتقييم"""
    safe_score = max(0, min(100, score if score is not None else 0))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=safe_score,
        title={'text': title, 'font': {'size': 18, 'color': '#FFFFFF'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#FFFFFF"},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 33], 'color': "rgba(255, 82, 82, 0.3)"},
                {'range': [33, 66], 'color': "rgba(255, 193, 7, 0.3)"},
                {'range': [66, 100], 'color': "rgba(0, 230, 118, 0.3)"}
            ]
        }
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
