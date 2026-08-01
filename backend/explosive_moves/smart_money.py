# backend/explosive_moves/smart_money.py
"""
محلل السيولة الذكية (Smart Money Analyzer Module)
يكشف تحركات السيولة الذكية وكبار المؤسسات (Accumulation/Distribution & VSA Patterns)
"""

from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd


class SmartMoneyAnalyzer:
    """تحليل سلوك السيولة الذكية باستخدام أنماط الحجم والسعر (Volume Spread Analysis)"""

    def __init__(self, lookback: int = 30):
        """
        Args:
            lookback: عدد الشموع السابقة المستخدمة في التحليل
        """
        self.lookback = lookback

    def _get_column(self, df: pd.DataFrame, col_name: str) -> pd.Series:
        """استخراج العمود بغض النظر عن حالة الأحرف (كبيرة/صغيرة)"""
        col_lower = col_name.lower()
        col_upper = col_name.capitalize()

        if col_lower in df.columns:
            return df[col_lower]
        elif col_upper in df.columns:
            return df[col_upper]
        elif col_name in df.columns:
            return df[col_name]
        return pd.Series(dtype=float)

    def analyze(self, df: pd.DataFrame) -> Dict[str, Union[float, bool, list, str]]:
        """تحليل حركة وتمركزات السيولة الذكية

        Returns:
            Dict يحتوي على درجة السيولة الذكية، ضغط الشراء/البيع، حالة التجميع/التوزيع، والأنماط المكتشفة
        """
        if df is None or df.empty or len(df) < self.lookback:
            return {'error': 'بيانات غير كافية لتحليل السيولة الذكية'}

        try:
            close = self._get_column(df, 'close')
            high = self._get_column(df, 'high')
            low = self._get_column(df, 'low')
            volume = self._get_column(df, 'volume')

            if close.empty or high.empty or low.empty or volume.empty:
                return {'error': 'أعمدة الأسعار والحجم غير مكتملة'}

            # 1. حساب ضغط الشراء والبيع
            buy_pressure, sell_pressure = self._calculate_pressure(df)

            # 2. كشف التراكم (Accumulation) والتوزيع (Distribution)
            accumulation = self._detect_accumulation(df)
            distribution = self._detect_distribution(df)

            # 3. كشف أنماط VSA
            patterns = self._detect_patterns(df)

            # 4. حساب درجة السيولة الذكية (0 - 100)
            smart_score = self._calculate_smart_score(
                buy_pressure, sell_pressure, accumulation, distribution, patterns
            )

            # 5. بناء التقرير والإشارة
            signal = self._get_signal(smart_score, accumulation, distribution)

            return {
                'smart_money_score': round(float(smart_score), 2),
                'accumulation': bool(accumulation),
                'distribution': bool(distribution),
                'buy_pressure': round(float(buy_pressure), 2),
                'sell_pressure': round(float(sell_pressure), 2),
                'patterns': patterns,
                'signal': signal,
            }

        except Exception as e:
            return {'error': f'حدث خطأ أثناء تحليل السيولة الذكية: {str(e)}'}

    def _calculate_pressure(self, df: pd.DataFrame) -> Tuple[float, float]:
        """حساب ضغط الشراء والبيع بناءً على أحجام التداول الحجمية"""
        close = self._get_column(df, 'close')
        volume = self._get_column(df, 'volume')

        window = min(len(df), 20)
        recent_close = close.iloc[-window:]
        recent_volume = volume.iloc[-window:]

        price_diff = recent_close.diff()

        # أحجام الأيام الصاعدة vs الهابطة
        buying_volume = recent_volume[price_diff > 0].sum()
        selling_volume = recent_volume[price_diff < 0].sum()

        total_volume = buying_volume + selling_volume

        if total_volume > 0:
            buy_pressure = (buying_volume / total_volume) * 100.0
            sell_pressure = (selling_volume / total_volume) * 100.0
        else:
            buy_pressure = 50.0
            sell_pressure = 50.0

        return buy_pressure, sell_pressure

    def _detect_accumulation(self, df: pd.DataFrame) -> bool:
        """كشف مرحلة التجميع (امتصاص العروض بحجم مرتفع واستقرار السعر)"""
        close = self._get_column(df, 'close')
        volume = self._get_column(df, 'volume')

        window = min(len(df), 15)
        recent_close = close.iloc[-window:]
        recent_volume = volume.iloc[-window:]

        avg_vol = volume.mean()

        # الشراء عند الانخفاض / الامتصاص: انخفاض ضئيل في السعر مع أحجام فاعلة أعلى من المتوسط
        price_change = recent_close.pct_change()
        absorption_candles = (price_change > -0.015) & (price_change < 0.005) & (recent_volume > avg_vol * 1.2)

        return int(absorption_candles.sum()) >= 2

    def _detect_distribution(self, df: pd.DataFrame) -> bool:
        """كشف مرحلة التوزيع (تفريغ الكميات مع ضعف الصعود أو الهبوط الحاد بحجم ضخم)"""
        close = self._get_column(df, 'close')
        volume = self._get_column(df, 'volume')

        window = min(len(df), 15)
        recent_close = close.iloc[-window:]
        recent_volume = volume.iloc[-window:]

        avg_vol = volume.mean()

        price_change = recent_close.pct_change()

        # التوزيع: ارتفاعات طفيفة جداً مع حجم تداول هائل (عدم قدرة على الدفع لأعلى) أو كسر هابط بحجم ضخم
        buying_climax = (price_change >= 0.0) & (price_change < 0.005) & (recent_volume > avg_vol * 1.5)
        heavy_selling = (price_change < -0.015) & (recent_volume > avg_vol * 1.3)

        distribution_signals = buying_climax | heavy_selling
        return int(distribution_signals.sum()) >= 2

    def _detect_patterns(self, df: pd.DataFrame) -> List[str]:
        """كشف أنماط سلوك كبار السلسلة (VSA Patterns)"""
        patterns = []
        close = self._get_column(df, 'close')
        high = self._get_column(df, 'high')
        low = self._get_column(df, 'low')
        volume = self._get_column(df, 'volume')

        if len(df) < 20:
            return ["لا توجد بيانات كافية للأنماط"]

        avg_vol_20 = volume.iloc[-20:-1].mean()
        avg_range_20 = (high - low).iloc[-20:-1].mean()

        recent_range_5 = (high.iloc[-5:] - low.iloc[-5:]).mean()
        recent_vol_5 = volume.iloc[-5:].mean()

        # 1. نمط التجميع في نطاق ضيق (Narrow Range Absorption)
        if recent_vol_5 > avg_vol_20 * 1.3 and recent_range_5 < avg_range_20 * 0.6:
            patterns.append("تراكم في نطاق ضيق (امتصاص)")

        # 2. نمط الاختراق القوي بحجم مؤسسي
        last_vol = volume.iloc[-1]
        last_close = close.iloc[-1]

        if last_vol > avg_vol_20 * 1.8:
            if last_close > close.iloc[-6:-1].max():
                patterns.append("اختراق صاعد بحجم مؤسسي")
            elif last_close < close.iloc[-6:-1].min():
                patterns.append("كسر هابط بحجم مؤسسي")

        # 3. نمط شمعة الابتلاع / الانعكاس بحجم مرتفع
        if len(df) >= 2:
            prev_close = close.iloc[-2]
            if last_close > prev_close * 1.015 and last_vol > volume.iloc[-2] * 1.25:
                patterns.append("اندفاع شرائي قوي")
            elif last_close < prev_close * 0.985 and last_vol > volume.iloc[-2] * 1.25:
                patterns.append("اندفاع بيعي قوي")

        return patterns if patterns else ["لا توجد أنماط واضحة"]

    def _calculate_smart_score(
        self,
        buy: float,
        sell: float,
        accumulation: bool,
        distribution: bool,
        patterns: List[str],
    ) -> float:
        """حساب درجة المحفظة والسيولة الذكية"""
        score = 50.0  # القيمة المحايدة

        # تأثير ضغط التداول
        if buy > 60:
            score += 15.0
        elif sell > 60:
            score -= 15.0

        # تأثير التراكم / التوزيع
        if accumulation:
            score += 20.0
        if distribution:
            score -= 20.0

        # تأكيد الأنماط
        bullish_patterns = [p for p in patterns if "صاعد" in p or "شرائي" in p or "تراكم" in p]
        bearish_patterns = [p for p in patterns if "هابط" in p or "بيعي" in p]

        score += len(bullish_patterns) * 7.0
        score -= len(bearish_patterns) * 7.0

        return float(np.clip(score, 0.0, 100.0))

    def _get_signal(self, score: float, accumulation: bool, distribution: bool) -> str:
        """تحديد توصية وإشارة السيولة الذكية"""
        if score >= 75 and accumulation:
            return "شراء قوي (تراكم مؤسسي)"
        elif score >= 60:
            return "شراء"
        elif score <= 25 and distribution:
            return "بيع قوي (توزيع مؤسسي)"
        elif score <= 40:
            return "بيع"
        else:
            return "محايد"
