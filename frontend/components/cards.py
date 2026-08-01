# frontend/components/cards.py
"""
بطاقات المعلومات والعرض
"""

import streamlit as st

def metric_card(icon, value, label, color=None):
    """عرض بطاقة مترو"""
    color_style = f"color:{color};" if color else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="icon">{icon}</div>
        <div class="value" style="{color_style}">{value}</div>
        <div class="label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def stock_card(symbol, name, sector, details=None):
    """عرض بطاقة سهم"""
    details_html = ""
    if details:
        for key, value in details.items():
            details_html += f"<span style='margin-right:15px;'><strong>{key}:</strong> {value}</span>"
    
    st.markdown(f"""
    <div class="stock-card">
        <h3>{symbol} - {name}</h3>
        <p>🏢 {sector}</p>
        {details_html}
    </div>
    """, unsafe_allow_html=True)

def status_badge(status, text):
    """عرض شارة الحالة"""
    status_class = {
        'buy': 'buy',
        'hold': 'hold',
        'sell': 'sell',
        'قوي': 'buy',
        'متوسط': 'hold',
        'ضعيف': 'sell'
    }.get(status, '')
    
    st.markdown(f"""
    <span class="status-badge {status_class}">{text}</span>
    """, unsafe_allow_html=True)
