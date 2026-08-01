# backend/explosive_moves/smart_money.py
"""
محلل السيولة الذكية (Smart Money Analyzer)
يكشف تحركات السيولة الذكية والكبار
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class SmartMoneyAnalyzer:
    """
    تحليل سلوك السيولة الذكية باستخدام أنماط الحجم والسعر
    """
    
    def __init__(self, lookback: int = 30):
        self.lookback = lookback
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        تحليل السيولة الذكية
        
        Returns:
            قاموس يحتوي على:
            - smart_money_score: float (0-100)
            - accumulation: bool
            - distribution: bool
            - buy_pressure: float
            - sell_pressure: float
            - patterns: List[str]
        """
        if df.empty or len(df) < self.lookback:
            return {'error': 'بيانات غير كافية'}
        
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            # حساب ضغط الشراء والبيع
            buy_pressure, sell_pressure = self._calculate_pressure(df)
            
            # كشف التراكم
            accumulation = self._detect_accumulation(df)
            
            # كشف التوزيع
            distribution = self._detect_distribution(df)
            
            # الأنماط
            patterns = self._detect_patterns(df)
            
            # حساب درجة السيولة الذكية
            smart_score = self._calculate_smart_score(
                buy_pressure, sell_pressure, accumulation, distribution, patterns
            )
            
            return {
                'smart_money_score': round(smart_score, 2),
                'accumulation': accumulation,
                'distribution': distribution,
                'buy_pressure': round(buy_pressure, 2),
                'sell_pressure': round(sell_pressure, 2),
                'patterns': patterns,
                'signal': self._get_signal(smart_score, accumulation, distribution)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_pressure(self, df: pd.DataFrame) -> Tuple[float, float]:
        """حساب ضغط الشراء والبيع"""
        close = df['Close']
        low = df['Low']
        high = df['High']
        volume = df['Volume']
        
        # مؤشر ضغط الشراء
        buying_volume = volume[close > close.shift()]
        selling_volume = volume[close < close.shift()]
        
        total_volume = volume.iloc[-20:].sum()
        buy_volume = buying_volume.iloc[-20:].sum()
        sell_volume = selling_volume.iloc[-20:].sum()
        
        buy_pressure = (buy_volume / total_volume * 100) if total_volume > 0 else 50
        sell_pressure = (sell_volume / total_volume * 100) if total_volume > 0 else 50
        
        return buy_pressure, sell_pressure
    
    def _detect_accumulation(self, df: pd.DataFrame) -> bool:
        """كشف التراكم (شراء تدريجي)"""
        close = df['Close']
        volume = df['Volume']
        
        # انخفاض في السعر مع زيادة في الحجم (شراء عند الانخفاض)
        price_down = close.pct_change() < -0.01
        volume_up = volume.pct_change() > 0.2
        
        accumulation_signals = (price_down & volume_up).iloc[-10:].sum()
        
        return accumulation_signals >= 3
    
    def _detect_distribution(self, df: pd.DataFrame) -> bool:
        """كشف التوزيع (بيع تدريجي)"""
        close = df['Close']
        volume = df['Volume']
        
        # ارتفاع في السعر مع زيادة في الحجم (بيع عند الارتفاع)
        price_up = close.pct_change() > 0.01
        volume_up = volume.pct_change() > 0.2
        
        distribution_signals = (price_up & volume_up).iloc[-10:].sum()
        
        return distribution_signals >= 3
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[str]:
        """كشف أنماط السيولة الذكية"""
        patterns = []
        close = df['Close']
        volume = df['Volume']
        
        # نمط 1: حجم مرتفع مع نطاق سعري ضيق
        recent_range = (df['High'].iloc[-5:] - df['Low'].iloc[-5:]).mean()
        avg_range = (df['High'] - df['Low']).iloc[-20:-5].mean()
        if volume.iloc[-5:].mean() > volume.iloc[-20:-5].mean() * 1.5:
            if recent_range < avg_range * 0.5:
                patterns.append("تراكم في نطاق ضيق")
        
        # نمط 2: كسر مع حجم مرتفع
        if volume.iloc[-1] > volume.iloc[-5:-1].mean() * 2:
            if close.iloc[-1] > close.iloc[-5:-1].max():
                patterns.append("كسر صاعد بحجم مرتفع")
            elif close.iloc[-1] < close.iloc[-5:-1].min():
                patterns.append("كسر هابط بحجم مرتفع")
        
        # نمط 3: شمعة انعكاس مع حجم
        if len(df) > 2:
            if close.iloc[-1] > close.iloc[-2] * 1.02:
                if volume.iloc[-1] > volume.iloc[-2] * 1.3:
                    patterns.append("شمعة صاعدة قوية")
            elif close.iloc[-1] < close.iloc[-2] * 0.98:
                if volume.iloc[-1] > volume.iloc[-2] * 1.3:
                    patterns.append("شمعة هابطة قوية")
        
        return patterns if patterns else ["لا توجد أنماط واضحة"]
    
    def _calculate_smart_score(self, buy: float, sell: float, 
                               accumulation: bool, distribution: bool,
                               patterns: List[str]) -> float:
        """حساب درجة السيولة الذكية"""
        score = 50  # قيمة محايدة
        
        # ضغط الشراء والبيع
        if buy > 60:
            score += 15
        elif sell > 60:
            score -= 15
        
        # التراكم والتوزيع
        if accumulation:
            score += 20
        if distribution:
            score -= 20
        
        # الأنماط
        if len(patterns) > 1:
            score += 10
        
        return max(0, min(100, score))
    
    def _get_signal(self, score: float, accumulation: bool, distribution: bool) -> str:
        """تحديد الإشارة بناءً على التحليل"""
        if score > 70 and accumulation:
            return "شراء قوي"
        elif score > 60 and accumulation:
            return "شراء"
        elif score < 30 and distribution:
            return "بيع قوي"
        elif score < 40 and distribution:
            return "بيع"
        else:
            return "محايد"
