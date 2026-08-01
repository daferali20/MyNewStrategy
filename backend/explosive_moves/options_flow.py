# backend/explosive_moves/options_flow.py
"""
محلل تدفق الخيارات (Options Flow Analyzer)
يحلل نشاط الخيارات للكشف عن تحركات السيولة الذكية
ملاحظة: هذا ملف اختياري ويعتمد على مصدر بيانات
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class OptionsFlowAnalyzer:
    """
    تحليل تدفق الخيارات - إصدار مبسط يعتمد على البيانات المتاحة
    """
    
    def __init__(self):
        self.calls = 0
        self.puts = 0
        self.unusual_activity = []
    
    def analyze(self, symbol: str, data: Dict = None) -> Dict:
        """
        تحليل تدفق الخيارات
        
        Args:
            symbol: رمز السهم
            data: بيانات الخيارات (اختياري)
        
        Returns:
            قاموس يحتوي على:
            - call_put_ratio: float
            - unusual_activity: bool
            - sentiment: str
            - total_volume: int
            - smart_money_score: float
        """
        # في حالة عدم توفر بيانات حقيقية، نستخدم بيانات محاكاة
        if data is None:
            data = self._generate_mock_data(symbol)
        
        try:
            calls = data.get('calls', 0)
            puts = data.get('puts', 0)
            total = calls + puts
            
            # نسبة Calls/Puts
            call_put_ratio = calls / puts if puts > 0 else 0
            
            # نشاط غير طبيعي
            unusual_activity = self._detect_unusual_activity(data)
            
            # المشاعر
            sentiment = self._get_sentiment(call_put_ratio)
            
            # درجة السيولة الذكية
            smart_score = self._calculate_smart_score(calls, puts, unusual_activity)
            
            return {
                'call_put_ratio': round(call_put_ratio, 2),
                'unusual_activity': unusual_activity,
                'sentiment': sentiment,
                'total_volume': total,
                'smart_money_score': round(smart_score, 2),
                'calls_volume': calls,
                'puts_volume': puts
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_mock_data(self, symbol: str) -> Dict:
        """توليد بيانات محاكاة للخيارات"""
        np.random.seed(hash(symbol) % 1000)
        
        # محاكاة أحجام الخيارات
        base_volume = np.random.randint(100, 5000)
        calls = base_volume + np.random.randint(-200, 200)
        puts = base_volume + np.random.randint(-200, 200)
        
        # نشاط غير طبيعي عشوائي
        unusual = np.random.random() > 0.7
        
        return {
            'calls': max(0, calls),
            'puts': max(0, puts),
            'unusual': unusual,
            'timestamp': pd.Timestamp.now()
        }
    
    def _detect_unusual_activity(self, data: Dict) -> bool:
        """كشف النشاط غير الطبيعي"""
        # في حالة البيانات الحقيقية، يتم مقارنة الحجم مع المتوسط
        return data.get('unusual', False)
    
    def _get_sentiment(self, ratio: float) -> str:
        """تحديد المشاعر بناءً على نسبة Calls/Puts"""
        if ratio > 1.5:
            return "صاعد بقوة"
        elif ratio > 1.0:
            return "صاعد"
        elif ratio > 0.7:
            return "محايد"
        elif ratio > 0.5:
            return "هابط"
        else:
            return "هابط بقوة"
    
    def _calculate_smart_score(self, calls: float, puts: float, unusual: bool) -> float:
        """حساب درجة السيولة الذكية من الخيارات"""
        score = 50
        
        # نسبة Calls/Puts مرتفعة تشير إلى ثقة
        if calls > puts * 1.5:
            score += 20
        elif puts > calls * 1.5:
            score -= 20
        
        # نشاط غير طبيعي يزيد الوزن
        if unusual:
            if calls > puts:
                score += 15
            else:
                score -= 15
        
        return max(0, min(100, score))
    
    def get_option_summary(self, symbol: str) -> pd.DataFrame:
        """الحصول على ملخص الخيارات"""
        result = self.analyze(symbol)
        if 'error' in result:
            return pd.DataFrame()
        
        return pd.DataFrame({
            'symbol': [symbol],
            'call_put_ratio': [result['call_put_ratio']],
            'sentiment': [result['sentiment']],
            'smart_score': [result['smart_money_score']],
            'unusual_activity': [result['unusual_activity']]
        })
