# backend/explosive_moves/compression.py
"""
محلل الانضغاط (Compression Analyzer)
يحلل فترات الانضغاط السعري ويحدد احتمالية الانفجار
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class CompressionAnalyzer:
    """
    تحليل الانضغاط باستخدام أنماط السعر والتقلبات المنخفضة
    """
    
    def __init__(self, lookback: int = 30, compression_threshold: float = 0.3):
        self.lookback = lookback
        self.compression_threshold = compression_threshold
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        تحليل الانضغاط
        
        Returns:
            قاموس يحتوي على:
            - is_compressed: bool
            - compression_score: float (0-100)
            - compression_days: int
            - price_range_percent: float
            - volume_decline: bool
            - pattern: str
        """
        if df.empty or len(df) < self.lookback:
            return {'error': 'بيانات غير كافية'}
        
        try:
            high = df['High']
            low = df['Low']
            close = df['Close']
            volume = df['Volume']
            
            # نطاق السعر خلال الفترة
            recent_high = high.iloc[-self.lookback:].max()
            recent_low = low.iloc[-self.lookback:].min()
            current_price = close.iloc[-1]
            
            price_range = recent_high - recent_low
            price_range_percent = (price_range / current_price) * 100
            
            # تحديد الانضغاط
            is_compressed = price_range_percent < self.compression_threshold
            
            # أيام الانضغاط
            compression_days = 0
            for i in range(self.lookback - 1, 0, -1):
                day_range = (high.iloc[i] - low.iloc[i]) / close.iloc[i] * 100
                if day_range < self.compression_threshold:
                    compression_days += 1
                else:
                    break
            
            # تحليل حجم التداول
            avg_volume = volume.iloc[-self.lookback:-1].mean()
            current_volume = volume.iloc[-1]
            volume_decline = current_volume < avg_volume * 0.8
            
            # أنماط الانضغاط
            pattern = self._identify_pattern(df)
            
            # درجة الانضغاط
            if is_compressed:
                # كلما زادت أيام الانضغاط، زادت الدرجة
                days_score = min(100, compression_days * 8)
                range_score = max(0, 100 - (price_range_percent / 0.3) * 100)
                compression_score = (days_score * 0.6 + range_score * 0.4)
            else:
                compression_score = max(0, 100 - (price_range_percent / 0.3) * 30)
            
            compression_score = min(100, max(0, compression_score))
            
            return {
                'is_compressed': is_compressed,
                'compression_score': round(compression_score, 2),
                'compression_days': compression_days,
                'price_range_percent': round(price_range_percent, 2),
                'volume_decline': volume_decline,
                'pattern': pattern,
                'recent_high': round(recent_high, 2),
                'recent_low': round(recent_low, 2),
                'current_price': round(current_price, 2)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _identify_pattern(self, df: pd.DataFrame) -> str:
        """تحديد نمط الانضغاط"""
        close = df['Close']
        
        # اتجاه السعر
        sma_50 = close.rolling(50).mean()
        current_price = close.iloc[-1]
        
        if current_price > sma_50.iloc[-1]:
            direction = "صاعد"
        elif current_price < sma_50.iloc[-1]:
            direction = "هابط"
        else:
            direction = "جانبي"
        
        # شكل الانضغاط
        recent_high = df['High'].iloc[-10:].max()
        recent_low = df['Low'].iloc[-10:].min()
        price_range = recent_high - recent_low
        avg_range = (df['High'] - df['Low']).iloc[-10:].mean()
        
        if price_range < avg_range * 0.5:
            shape = "مثلث مضيق"
        elif price_range < avg_range * 0.8:
            shape = "قناة ضيقة"
        else:
            shape = "انضغاط عادي"
        
        return f"{direction} - {shape}"
    
    def get_compression_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """الحصول على إشارات الانضغاط"""
        result = self.analyze(df)
        if 'error' in result:
            return pd.DataFrame()
        
        return pd.DataFrame({
            'compression_score': [result['compression_score']],
            'is_compressed': [result['is_compressed']],
            'compression_days': [result['compression_days']],
            'price_range_percent': [result['price_range_percent']],
            'pattern': [result['pattern']]
        })
