# backend/explosive_moves/options_flow.py
"""
محلل تدفق الخيارات (Options Flow Analyzer Module)
يحلل نشاط العقود والخيارات لكشف تحركات وتمركزات السيولة الذكية (Smart Money)
"""

from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd


class OptionsFlowAnalyzer:
    """تحليل تدفق الخيارات وتتبع النشاط المؤسسي غير الطبيعي (Unusual Options Activity)"""

    def __init__(self):
        self.calls = 0
        self.puts = 0
        self.unusual_activity = []

    def analyze(self, symbol: str, data: Optional[Dict] = None) -> Dict[str, Union[float, int, bool, str]]:
        """تحليل تدفق الخيارات لرمز معين

        Args:
            symbol: رمز السهم (مثل 'AAPL', 'NVDA')
            data: بيانات الخيارات الفعلية (اختياري، يتم توليد بيانات محاكاة عند غيابه)

        Returns:
            Dict يحتوي على نسبة Call/Put، درجة السيولة الذكية، والانحرافات المكتشفة
        """
        if not symbol:
            return {'error': 'رمز السهم غير صالح'}

        # استخدام بيانات محاكاة مبنية على الرمز عند غياب البيانات المباشرة
        if data is None or not isinstance(data, dict):
            data = self._generate_mock_data(symbol)

        try:
            calls = int(data.get('calls', 0))
            puts = int(data.get('puts', 0))
            total_volume = calls + puts

            # حساب نسبة Call / Put الحقيقية مع منع القسمة على الصفر
            if puts > 0:
                call_put_ratio = calls / puts
            elif calls > 0:
                call_put_ratio = 10.0  # نسبة مرتفعة جداً تعكس سيطرة شرائية تامة
            else:
                call_put_ratio = 1.0  # محايد في حالة غياب التداول

            # كشف النشاط غير الطبيعي (Unusual Options Activity)
            unusual_activity = self._detect_unusual_activity(data)

            # تحديد الاتجاه العام للمشاعر (Sentiment)
            sentiment = self._get_sentiment(call_put_ratio)

            # حساب درجة السيولة الذكية (Options Score / Smart Money Score 0-100)
            smart_score = self._calculate_smart_score(calls, puts, unusual_activity)

            return {
                'symbol': symbol,
                'call_put_ratio': round(float(call_put_ratio), 2),
                'unusual_activity': bool(unusual_activity),
                'sentiment': sentiment,
                'total_volume': int(total_volume),
                'smart_money_score': round(float(smart_score), 2),
                'options_score': round(float(smart_score), 2),  # للتوافق المباشر مع ExplosiveScore
                'calls_volume': int(calls),
                'puts_volume': int(puts),
            }

        except Exception as e:
            return {'error': f'حدث خطأ أثناء تحليل تدفق الخيارات: {str(e)}'}

    def _generate_mock_data(self, symbol: str) -> Dict:
        """توليد بيانات خيارات محاكاة مستقرة مبنية على الرمز"""
        # استخدام abs لضمان seed موجب دائماً
        seed_val = abs(hash(symbol)) % 100000
        rs = np.random.RandomState(seed_val)

        base_volume = rs.randint(500, 10000)
        calls_var = rs.randint(-300, 500)
        puts_var = rs.randint(-300, 500)

        calls = max(50, base_volume + calls_var)
        puts = max(50, base_volume + puts_var)

        # احتمال كشف نشاط غير عادي
        unusual = bool(rs.random() > 0.65)

        return {
            'calls': calls,
            'puts': puts,
            'unusual': unusual,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _detect_unusual_activity(self, data: Dict) -> bool:
        """كشف العمليات ذات الأحجام الضخمة والنشاط غير المعتاد"""
        return bool(data.get('unusual', False))

    def _get_sentiment(self, ratio: float) -> str:
        """تحديد انطباع وتمركز المتداولين بناءً على نسبة العقود"""
        if ratio >= 1.8:
            return "صاعد بقوة 🚀"
        elif ratio >= 1.2:
            return "صاعد 📈"
        elif ratio >= 0.8:
            return "محايد 📊"
        elif ratio >= 0.5:
            return "هابط 📉"
        else:
            return "هابط بقوة ⚠️"

    def _calculate_smart_score(self, calls: int, puts: int, unusual: bool) -> float:
        """حساب درجة تفوق السيولة الذكية (0 - 100)"""
        score = 50.0

        total = calls + puts
        if total == 0:
            return 50.0

        call_ratio = calls / total

        # تعديل النقطة بناءً على غلبة عقود الكول
        if call_ratio > 0.65:
            score += 25.0 * (call_ratio - 0.5) * 2
        elif call_ratio < 0.35:
            score -= 25.0 * (0.5 - call_ratio) * 2

        # تأثير النشاط غير الطبيعي
        if unusual:
            if calls > puts:
                score += 15.0
            else:
                score -= 15.0

        return float(np.clip(score, 0.0, 100.0))

    def get_option_summary(self, symbol: str) -> pd.DataFrame:
        """إرجاع ملخص الخيارات كـ DataFrame موحد"""
        result = self.analyze(symbol)
        if 'error' in result:
            return pd.DataFrame()

        return pd.DataFrame([
            {
                'symbol': result['symbol'],
                'call_put_ratio': result['call_put_ratio'],
                'sentiment': result['sentiment'],
                'smart_score': result['smart_money_score'],
                'unusual_activity': result['unusual_activity'],
                'calls_volume': result['calls_volume'],
                'puts_volume': result['puts_volume'],
            }
        ])
