# backend/explosive_moves/squeeze_detector.py
"""
كاشف الانضغاط السعري (Squeeze Detector)
يكتشف فترات انضغاط السعر التي تسبق الحركات المتفجرة
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional

class SqueezeDetector:
    """
    كشف انضغاط السعر باستخدام Bollinger Bands و Keltner Channels
    """
    
    def __init__(self, 
                 bb_period: int = 20,
                 bb_std: float = 2.0,
                 kc_period: int = 20,
                 kc_atr_multiplier: float = 1.5):
        """
        Args:
            bb_period: فترة Bollinger Bands
            bb_std: عدد الانحرافات المعيارية
            kc_period: فترة Keltner Channels
            kc_atr_multiplier: مضاعف ATR لـ Keltner
        """
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.kc_period = kc_period
        self.kc_atr_multiplier = kc_atr_multiplier
    
    def detect(self, df: pd.DataFrame) -> Dict:
        """
        كشف الانضغاط في البيانات
        
        Returns:
            قاموس يحتوي على:
            - is_squeeze: bool
            - squeeze_score: float (0-100)
            - bb_width: float
            - kc_width: float
            - ratio: float
            - squeeze_history: list
        """
        if df.empty or len(df) < self.bb_period:
            return {'error': 'بيانات غير كافية'}
        
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            
            # حساب Bollinger Bands
            bb_middle = close.rolling(self.bb_period).mean()
            bb_std = close.rolling(self.bb_period).std()
            bb_upper = bb_middle + (bb_std * self.bb_std)
            bb_lower = bb_middle - (bb_std * self.bb_std)
            bb_width = (bb_upper - bb_lower) / bb_middle
            
            # حساب Keltner Channels
            typical_price = (high + low + close) / 3
            kc_middle = typical_price.rolling(self.kc_period).mean()
            
            # ATR
            high_low = high - low
            high_close = abs(high - close.shift())
            low_close = abs(low - close.shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(14).mean()
            
            kc_upper = kc_middle + (atr * self.kc_atr_multiplier)
            kc_lower = kc_middle - (atr * self.kc_atr_multiplier)
            kc_width = (kc_upper - kc_lower) / kc_middle
            
            # كشف الانضغاط
            current_bb_width = bb_width.iloc[-1]
            current_kc_width = kc_width.iloc[-1]
            
            # حساب نسبة الانضغاط
            ratio = current_bb_width / current_kc_width
            
            # تاريخ الانضغاط
            squeeze_history = (bb_width < kc_width).astype(int).tolist()
            
            # درجة الانضغاط
            if ratio < 0.7:
                squeeze_score = 90 + (1 - ratio) * 33  # انضغاط شديد
            elif ratio < 0.9:
                squeeze_score = 60 + (0.9 - ratio) * 200
            elif ratio < 1.1:
                squeeze_score = 40 + (1.1 - ratio) * 200
            else:
                squeeze_score = max(0, 40 - (ratio - 1.1) * 100)
            
            squeeze_score = min(100, max(0, squeeze_score))
            
            # الحالة الحالية
            is_squeeze = current_bb_width < current_kc_width
            
            return {
                'is_squeeze': is_squeeze,
                'squeeze_score': round(squeeze_score, 2),
                'bb_width': round(current_bb_width, 4),
                'kc_width': round(current_kc_width, 4),
                'ratio': round(ratio, 3),
                'squeeze_history': squeeze_history[-50:],
                'bb_upper': round(bb_upper.iloc[-1], 2),
                'bb_lower': round(bb_lower.iloc[-1], 2),
                'kc_upper': round(kc_upper.iloc[-1], 2),
                'kc_lower': round(kc_lower.iloc[-1], 2)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_squeeze_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """الحصول على إشارات الانضغاط كـ DataFrame"""
        result = self.detect(df)
        if 'error' in result:
            return pd.DataFrame()
        
        return pd.DataFrame({
            'squeeze_score': [result['squeeze_score']],
            'is_squeeze': [result['is_squeeze']],
            'bb_width': [result['bb_width']],
            'kc_width': [result['kc_width']],
            'ratio': [result['ratio']]
        })
