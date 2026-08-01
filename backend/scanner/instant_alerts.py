#backend/scanner/instant_alerts.py

import yfinance as yf
import pandas as pd

def check_instant_breakout(ticker_symbol: str) -> dict:
    """
    فحص التغيرات اللحظية للسهم على إطار 5 دقائق لرصد بداية السيولة
    """
    try:
        # جلب بيانات 5 دقائق لآخر يومين
        df = yf.Ticker(ticker_symbol).history(period="2d", interval="5m")
        
        if df.empty or len(df) < 20:
            return None
            
        latest_candle = df.iloc[-1]
        prev_candles = df.iloc[-21:-1]
        
        # 1. حساب متوسط الفوليوم لآخر 20 شمعة (كل شمعة 5 دقائق)
        avg_vol = prev_candles['Volume'].mean()
        current_vol = latest_candle['Volume']
        
        # 2. هل الفوليوم الحالي أعلى بـ 3 أضعاف من المتوسط؟
        vol_spike = current_vol >= (avg_vol * 3.0) if avg_vol > 0 else False
        
        # 3. هل الشمعة الحالية خضراء وقوية؟
        price_change = ((latest_candle['Close'] - latest_candle['Open']) / latest_candle['Open']) * 100
        strong_green = price_change > 1.5  # صعود أكثر من 1.5% في 5 دقائق
        
        if vol_spike and strong_green:
            return {
                "symbol": ticker_symbol,
                "price": round(latest_candle['Close'], 2),
                "volume_ratio": round(current_vol / avg_vol, 1),
                "5m_change": f"+{round(price_change, 2)}%",
                "status": "🚀 بدء انفجار/دخول سيولة مفاجئ!"
            }
            
    except Exception:
        return None
        
    return None
