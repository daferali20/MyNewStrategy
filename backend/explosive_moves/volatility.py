# backend/explosive_moves/volatility.py
"""
محلل التقلبات (Volatility Analyzer)
يحلل التقلبات السعرية ويتنبأ بالتغيرات المفاجئة
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class VolatilityAnalyzer:
    """
    تحليل التقلبات باستخدام ATR، Bollinger Bands، والتقلبات التاريخية
    """
    
    def __init__(self, atr_period: int = 14, lookback: int = 20):
        self.atr_period = atr_period
        self.lookback = lookback
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        تحليل التقلبات
        
        Returns:
            قاموس يحتوي على:
            - current_atr: float
            - atr_percent: float
            - volatility_ratio: float
            - historical_volatility: float
            - volatility_breakout: bool
            - volatility_score: float (0-100)
        """
        if df.empty or len(df) < self.lookback:
            return {'error': 'بيانات غير كافية'}
        
        try:
            high = df['High']
            low = df['Low']
            close = df['Close']
            
            # حساب ATR
            high_low = high - low
            high_close = abs(high - close.shift())
            low_close = abs(low - close.shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(self.atr_period).mean()
            
            current_atr = atr.iloc[-1]
            current_price = close.iloc[-1]
            atr_percent = (current_atr / current_price) * 100
            
            # التقلبات التاريخية
            returns = close.pct_change().dropna()
            historical_vol = returns.rolling(self.lookback).std() * np.sqrt(252) * 100
            current_hist_vol = historical_vol.iloc[-1] if not historical_vol.isna().iloc[-1] else 0
            
            # متوسط التقلبات
            avg_atr = atr.iloc[-self.lookback:-1].mean()
            volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1
            
            # تحديد انفجار التقلبات
            volatility_breakout = volatility_ratio > 1.5
            
            # حساب درجة التقلبات
            if volatility_ratio > 2.0:
                vol_score = 90 + min(10, (volatility_ratio - 2) * 10)
            elif volatility_ratio > 1.5:
                vol_score = 70 + (volatility_ratio - 1.5) * 40
            elif volatility_ratio > 1.0:
                vol_score = 50 + (volatility_ratio - 1) * 40
            else:
                vol_score = max(0, 50 - (1 - volatility_ratio) * 50)
            
            vol_score = min(100, max(0, vol_score))
            
            # حساب Bollinger Bands للتقلبات
            bb_middle = close.rolling(20).mean()
            bb_std = close.rolling(20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            bb_width = (bb_upper - bb_lower) / bb_middle
            
            return {
                'current_atr': round(current_atr, 2),
                'atr_percent': round(atr_percent, 2),
                'volatility_ratio': round(volatility_ratio, 2),
                'historical_volatility': round(current_hist_vol, 2),
                'volatility_breakout': volatility_breakout,
                'volatility_score': round(vol_score, 2),
                'bb_width': round(bb_width.iloc[-1], 4),
                'current_price': round(current_price, 2)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_volatility_breakouts(self, df: pd.DataFrame, threshold: float = 1.5) -> pd.DataFrame:
        """الحصول على نقاط انفجار التقلبات"""
        result = self.analyze(df)
        if 'error' in result:
            return pd.DataFrame()
        
        return pd.DataFrame({
            'volatility_score': [result['volatility_score']],
            'volatility_ratio': [result['volatility_ratio']],
            'volatility_breakout': [result['volatility_breakout']],
            'atr_percent': [result['atr_percent']]
        })
