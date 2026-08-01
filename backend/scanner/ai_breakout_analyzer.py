# backend/scanner/ai_breakout_analyzer.py
"""
ماسح الانفجار بالذكاء الاصطناعي
"""

import pandas as pd
from config import STOCK_SYMBOLS
from frontend.utils.helpers import get_stock_data_cached, get_stock_info_cached

def scan_market_ai(sector=None, min_score=60, min_prob=55, max_symbols=20):
    """
    مسح السوق باستخدام الذكاء الاصطناعي
    """
    symbols = STOCK_SYMBOLS
    results = []
    
    for symbol in symbols[:max_symbols]:
        try:
            df = get_stock_data_cached(symbol, period="6mo")
            if df.empty or len(df) < 50:
                continue
            
            analysis = analyze_stock(df, symbol)
            
            if analysis and analysis['squeeze_score'] >= min_score and analysis['breakout_probability'] >= min_prob:
                # فلترة حسب القطاع
                if sector:
                    info = get_stock_info_cached(symbol)
                    if info.get('sector') != sector:
                        continue
                
                results.append(analysis)
                
        except Exception:
            continue
    
    return pd.DataFrame(results)

def analyze_stock(df, symbol):
    """تحليل سهم فردي"""
    close = df['Close']
    volume = df['Volume']
    
    # حساب مؤشرات فنية
    sma_20 = close.rolling(20).mean()
    std_20 = close.rolling(20).std()
    bb_upper = sma_20 + (std_20 * 2)
    bb_lower = sma_20 - (std_20 * 2)
    bandwidth = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma_20.iloc[-1] if sma_20.iloc[-1] > 0 else 0
    
    # درجة الضغط
    min_bandwidth = ((bb_upper - bb_lower) / sma_20).iloc[-50:-1].min() if len(df) > 50 else bandwidth
    squeeze_score = max(0, min(100, ((1 - bandwidth / min_bandwidth) * 100) if min_bandwidth > 0 else 50))
    
    # حجم التداول
    avg_volume = volume.iloc[-21:-1].mean() if len(volume) > 21 else volume.mean()
    volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
    
    # احتمالية الانفجار
    breakout_prob = min(100, (squeeze_score * 0.5 + min(volume_ratio * 20, 50)))
    
    # معلومات الشركة
    info = get_stock_info_cached(symbol)
    name = info.get('longName', symbol)
    sector_name = info.get('sector', 'غير معروف')
    
    current_price = close.iloc[-1]
    high = df['High'].iloc[-20:].max()
    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or current_price * 0.02
    
    return {
        'symbol': symbol,
        'name': name[:35],
        'sector': sector_name,
        'current_price': round(current_price, 2),
        'squeeze_score': round(squeeze_score, 2),
        'breakout_probability': round(breakout_prob, 2),
        'expected_upside': round(((high + (atr * 2) - current_price) / current_price) * 100, 2),
        'risk_level': 'منخفض' if squeeze_score > 70 and volume_ratio > 1.5 else 'متوسط' if squeeze_score > 50 else 'مرتفع',
        'time_to_breakout': 'قريباً' if squeeze_score > 75 else 'خلال أيام' if squeeze_score > 60 else 'أسبوع',
        'entry_point': round(high + (atr * 0.5), 2),
        'stop_loss': round(current_price - (atr * 1.5), 2),
        'target_1': round(current_price + (atr * 2), 2),
        'target_2': round(current_price + (atr * 3.5), 2),
        'volume_ratio': round(volume_ratio, 2)
    }
