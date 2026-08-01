# frontend/components/charts.py
"""
مكونات الرسوم البيانية
"""

import plotly.graph_objects as go

def create_candlestick_chart(df, symbol, entry_points=None):
    """إنشاء رسم بياني للشموع اليابانية"""
    
    fig = go.Figure()
    
    # الشموع
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="السعر"
    ))
    
    # المتوسطات المتحركة
    if len(df) > 20:
        ma20 = df['Close'].rolling(window=20).mean()
        ma50 = df['Close'].rolling(window=50).mean() if len(df) > 50 else None
        
        fig.add_trace(go.Scatter(
            x=df.index, y=ma20,
            line=dict(color='#FFD700', width=1.5),
            name="MA20"
        ))
        
        if ma50 is not None:
            fig.add_trace(go.Scatter(
                x=df.index, y=ma50,
                line=dict(color='#FF6B6B', width=1.5),
                name="MA50"
            ))
    
    # مستويات الدخول والخروج
    if entry_points:
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
    
    # تنسيق الرسم
    fig.update_layout(
        title=f"📈 {symbol} - رسم بياني فني",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig


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
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig
