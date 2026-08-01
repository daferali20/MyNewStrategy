# frontend/components/cards.py
"""
بطاقات المعلومات والعرض - Cards & Badges Component
مُصلح ومُحسن بالكامل مع دعم التنسيق العربي وFlexbox
"""

import streamlit as st
import html

def metric_card(icon: str, value: str, label: str, color: str = None):
    """
    عرض بطاقة إحصائيات (Metric Card)
    
    :param icon: أيقونة البطاقة (مثل: 📈, 🔥)
    :param value: القيمة الرقمية أو النصية المراد عرضها
    :param label: التسمية التوضيحية للبطاقة
    :param color: لون القيمة (اختياري)
    """
    color_style = f"color:{color};" if color else ""
    safe_value = html.escape(str(value))
    safe_label = html.escape(str(label))
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="icon">{icon}</div>
        <div class="value" style="{color_style}">{safe_value}</div>
        <div class="label">{safe_label}</div>
    </div>
    """, unsafe_allow_html=True)

def stock_card(symbol: str, name: str, sector: str, details: dict = None):
    """
    عرض بطاقة سهم تفاعلية مع التفاصيل
    
    :param symbol: رمز السهم (مثل: AAPL)
    :param name: اسم الشركة
    :param sector: قطاع الشركة
    :param details: قاموس يتضمن التفاصيل الفنية (مثل: {'السعر': '$175.34', 'الهدف': '$190.00'})
    """
    safe_symbol = html.escape(str(symbol))
    safe_name = html.escape(str(name))
    safe_sector = html.escape(str(sector))
    
    details_html = ""
    if details and isinstance(details, dict):
        details_items = []
        for key, value in details.items():
            k_safe = html.escape(str(key))
            v_safe = html.escape(str(value))
            details_items.append(
                f'<div style="background: rgba(255,255,255,0.05); padding: 5px 10px; border-radius: 6px;">'
                f'<strong>{k_safe}:</strong> {v_safe}</div>'
            )
        details_html = f'<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">{"".join(details_items)}</div>'

    st.markdown(f"""
    <div class="stock-card" style="border: 1px solid rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 12px;">
        <h3 style="margin: 0 0 5px 0;">{safe_symbol} <span style="font-size: 0.8em; opacity: 0.8;">({safe_name})</span></h3>
        <p style="margin: 0; color: #888;">🏢 القطاع: {safe_sector}</p>
        {details_html}
    </div>
    """, unsafe_allow_html=True)

def status_badge(status: str, text: str):
    """
    عرض شارة الحالة (Status Badge)
    
    :param status: نوع الحالة ('buy', 'hold', 'sell', 'قوي', 'متوسط', 'ضعيف')
    :param text: النص المكتوب داخل الشارة
    """
    status_key = str(status).lower().strip()
    status_class = {
        'buy': 'buy',
        'hold': 'hold',
        'sell': 'sell',
        'قوي': 'buy',
        'شراء': 'buy',
        'متوسط': 'hold',
        'انتظار': 'hold',
        'ضعيف': 'sell',
        'بيع': 'sell'
    }.get(status_key, 'hold')
    
    safe_text = html.escape(str(text))
    
    st.markdown(f"""
    <span class="status-badge {status_class}">{safe_text}</span>
    """, unsafe_allow_html=True)
