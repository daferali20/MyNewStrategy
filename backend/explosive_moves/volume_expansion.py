# backend/explosive_moves/volume_expansion.py
"""
محلل توسع حجم التداول (Volume Expansion)
يكشف التوسع غير الطبيعي في أحجام التداول
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class VolumeExpansion:
    """
    تحليل حجم التداول والكشف عن التوسع غير الطبيعي
    """
    
    def __init__(self, lookback: int = 20, surge_threshold: float = 1.5):
        self.lookback = lookback
        self.surge_threshold = surge_threshold
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        تحليل توسع الحجم
        
        Returns:
            قاموس يحتوي على:
            - volume_ratio: float
            - is_surge: bool
            - surge_strength: float (0-100)
            - volume_trend: str
            - average_volume: float
            - current_volume: float
        """
        if df.empty or len(df) < self.lookback:
            return {'error': 'بيانات غير كافية'}
        
        try:
            volume = df['Volume']
            
            # متوسط الحجم
            avg_volume = volume.iloc[-self.lookback:-1].mean()
            current_volume = volume.iloc[-1]
            
            # نسبة الحجم الحالي إلى المتوسط
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # كشف الاندفاع
            is_surge = volume_ratio >= self.surge_threshold
            
            # قوة الاندفاع
            if volume_ratio > 3.0:
                surge_strength = 100
            elif volume_ratio > 2.0:
                surge_strength = 70 + (volume_ratio - 2) * 30
            elif volume_ratio > 1.5:
                surge_strength = 50 + (volume_ratio - 1.5) * 40
            else:
                surge_strength = max(0, volume_ratio / 1.5 * 50)
            
            surge_strength = min(100, max(0, surge_strength))
            
            # اتجاه الحجم
            volume_ma = volume.rolling(10).mean()
            volume_trend = self._get_volume_trend(volume, volume_ma)
            
            # حجم التداول الذكي
            smart_volume = self._detect_smart_volume(df)
            
            return {
                'volume_ratio': round(volume_ratio, 2),
                'is_surge': is_surge,
                'surge_strength': round(surge_strength, 2),
                'volume_trend': volume_trend,
                'average_volume': round(avg_volume, 0),
                'current_volume': round(current_volume, 0),
                'smart_volume': smart_volume,
                'is_smart_money': smart_volume > 50
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_volume_trend(self, volume: pd.Series, volume_ma: pd.Series) -> str:
        """تحديد اتجاه الحجم"""
        if len(volume) < 20:
            return 'غير محدد'
        
        recent = volume.iloc[-10:].mean()
        older = volume.iloc[-20:-10].mean()
        
        ratio = recent / older if older > 0 else 1
        
        if ratio > 1.3:
            return 'صاعد'
        elif ratio < 0.7:
            return 'هابط'
        else:
            return 'جانبي'
    
    def _detect_smart_volume(self, df: pd.DataFrame) -> float:
        """
        كشف حجم التداول الذكي (السيولة الذكية)
        """
        volume = df['Volume']
        close = df['Close']
        
        # تغير السعر مع الحجم
        price_change = close.pct_change()
        volume_change = volume.pct_change()
        
        # حساب معامل العلاقة
        correlation = price_change.iloc[-20:].corr(volume_change.iloc[-20:]) if len(price_change) > 20 else 0
        
        # حجم غير طبيعي مع تغير سعر معتدل = سيولة ذكية
        smart_score = 0
        
        # حجم مرتفع مع تغير سعر صغير
        if volume.iloc[-1] > volume.iloc[-20:-1].mean() * 1.5:
            if abs(price_change.iloc[-1]) < 0.02:
                smart_score += 50
        
        # علاقة إيجابية قوية
        if correlation > 0.3:
            smart_score += 30
        
        # ثبات السعر مع زيادة الحجم
        if volume.iloc[-1] > volume.iloc[-10:-1].mean() * 1.3:
            if close.iloc[-1] > close.iloc[-10:-1].mean() * 0.98:
                if close.iloc[-1] < close.iloc[-10:-1].mean() * 1.02:
                    smart_score += 20
        
        return min(100, max(0, smart_score))
    
    def get_volume_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """الحصول على إشارات الحجم"""
        result = self.analyze(df)
        if 'error' in result:
            return pd.DataFrame()
        
        return pd.DataFrame({
            'volume_ratio': [result['volume_ratio']],
            'is_surge': [result['is_surge']],
            'surge_strength': [result['surge_strength']],
            'volume_trend': [result['volume_trend']],
            'is_smart_money': [result['is_smart_money']]
        })
