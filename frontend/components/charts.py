# frontend/components/charts.py
"""
مكونات الرسوم البيانية - تم إصلاح use_container_width
"""

import plotly.graph_objects as go

def create_candlestick_chart(df, symbol, entry_points=None):
    """إنشاء رسم بياني للشموع"""
    fig = go.Figure()
    
    # الشموع
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="السعر",
        increasing=dict(line=dict(color='#00E676')),
        decreasing=dict(line=dict(color='#FF5252'))
    ))
    
    # المتوسطات المتحركة
    if len(df) > 20:
        ma20 = df['Close'].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma20,
            line=dict(color='#FFD700', width=1.2),
            name="MA20",
            opacity=0.7
        ))
    
    if len(df) > 50:
        ma50 = df['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma50,
            line=dict(color='#29B6F6', width=1.2),
            name="MA50",
            opacity=0.7
        ))
    
    # مستويات الدخول والخروج
    if entry_points:
        add_levels(fig, entry_points)
    
    fig.update_layout(
        title=f"📈 {symbol} - تحليل فني",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500,
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
    
    return fig

def add_levels(fig, entry_points):
    """إضافة مستويات الدخول والخروج"""
    levels = [
        ('entry_point', '#00E676', 'نقطة الدخول', 'top right'),
        ('stop_loss', '#FF5252', 'وقف الخسارة', 'bottom right'),
        ('target_1', '#29B6F6', 'الهدف 1', 'top left'),
        ('target_2', '#AB47BC', 'الهدف 2', 'bottom left')
    ]
    for key, color, label, position in levels:
        if key in entry_points and entry_points[key]:
            fig.add_hline(
                y=entry_points[key],
                line_dash="dash",
                line_color=color,
                annotation_text=label,
                annotation_position=position
            )

def create_score_gauge(score, title="الدرجة"):
    """إنشاء مقياس للدرجة"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 33], 'color': "rgba(255, 82, 82, 0.3)"},
                {'range': [33, 66], 'color': "rgba(255, 193, 7, 0.3)"},
                {'range': [66, 100], 'color': "rgba(0, 230, 118, 0.3)"}
            ]
        }
    ))
    fig.update_layout(height=250)
    return fig
