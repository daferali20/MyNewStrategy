# backend/explosive_moves/volume_expansion.py
"""
محلل توسع حجم التداول (Volume Expansion Module)
يكشف التوسع غير الطبيعي في أحجام التداول والسيولة الذكية (Smart Money Flow)
"""

from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd


class VolumeExpansion:
    """تحليل حجم التداول والكشف عن التوسع غير الطبيعي والسيولة الذكية"""

    def __init__(self, lookback: int = 20, surge_threshold: float = 1.5):
        self.lookback = lookback
        self.surge_threshold = surge_threshold

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

    def analyze(self, df: pd.DataFrame) -> Dict[str, Union[float, bool, str]]:
        """تحليل توسع الحجم وتطبيق الخوارزميات الفنية

        Returns:
            Dict يحتوي على تفاصيل المقاييس الحسابية لإشارات حجم التداول
        """
        if df is None or df.empty or len(df) < self.lookback:
            return {'error': 'بيانات غير كافية للتحليل'}

        try:
            volume = self._get_column(df, 'volume')
            close = self._get_column(df, 'close')

            if volume.empty:
                return {'error': 'عمود حجم التداول (volume) غير متوفر'}

            # 1. متوسط الحجم للفترة وحساب النسبة
            avg_volume = volume.iloc[-self.lookback : -1].mean()
            current_volume = volume.iloc[-1]

            if pd.isna(avg_volume) or avg_volume <= 0:
                avg_volume = 1.0

            volume_ratio = current_volume / avg_volume
            volume_ratio = (
                float(np.nan_to_num(volume_ratio, nan=1.0, posinf=1.0))
                if not np.isinf(volume_ratio)
                else 5.0
            )

            # 2. كشف الاندفاع غير الطبيعي
            is_surge = bool(volume_ratio >= self.surge_threshold)

            # 3. قوة الاندفاع (Surge Strength)
            if volume_ratio > 3.0:
                surge_strength = 100.0
            elif volume_ratio > 2.0:
                surge_strength = 70.0 + (volume_ratio - 2.0) * 30.0
            elif volume_ratio > 1.5:
                surge_strength = 50.0 + (volume_ratio - 1.5) * 40.0
            else:
                surge_strength = max(0.0, (volume_ratio / 1.5) * 50.0)

            surge_strength = float(min(100.0, max(0.0, surge_strength)))

            # 4. اتجاه الحجم
            volume_ma = volume.rolling(10, min_periods=1).mean()
            volume_trend = self._get_volume_trend(volume, volume_ma)

            # 5. كشف حجم التداول الذكي (Smart Money)
            smart_volume = self._detect_smart_volume(df)

            return {
                'volume_ratio': round(volume_ratio, 2),
                'is_surge': is_surge,
                'surge_strength': round(surge_strength, 2),
                'volume_trend': volume_trend,
                'average_volume': round(float(avg_volume), 0),
                'current_volume': round(float(current_volume), 0),
                'smart_volume': round(float(smart_volume), 2),
                'is_smart_money': bool(smart_volume > 50.0),
            }

        except Exception as e:
            return {'error': f'حدث خطأ في تحليل الحجم: {str(e)}'}

    def _get_volume_trend(
        self, volume: pd.Series, volume_ma: pd.Series
    ) -> str:
        """تحديد الاتجاه العام لحجم التداول"""
        if len(volume) < 20:
            return 'غير محدد'

        recent = volume.iloc[-10:].mean()
        older = volume.iloc[-20:-10].mean()

        ratio = (recent / older) if older > 0 else 1.0

        if ratio > 1.3:
            return 'صاعد'
        elif ratio < 0.7:
            return 'هابط'
        else:
            return 'جانبي'

    def _detect_smart_volume(self, df: pd.DataFrame) -> float:
        """كشف تدفقات السيولة الذكية (Smart Money Detection Algorithm)"""
        volume = self._get_column(df, 'volume')
        close = self._get_column(df, 'close')

        if volume.empty or close.empty or len(df) < 20:
            return 0.0

        # تغير السعر والحجم الحسابي
        price_change = close.pct_change().fillna(0)
        volume_change = volume.pct_change().fillna(0)

        # حساب معامل التلازم (Correlation)
        corr_series = price_change.iloc[-20:].corr(volume_change.iloc[-20:])
        correlation = float(np.nan_to_num(corr_series, nan=0.0))

        smart_score = 0.0

        # 1. حجم ضخم مع تغير طفيف في السعر (تجميع صامت/تفريغ)
        avg_vol_20 = volume.iloc[-20:-1].mean()
        if avg_vol_20 > 0 and volume.iloc[-1] > (avg_vol_20 * 1.5):
            if abs(price_change.iloc[-1]) < 0.02:
                smart_score += 50.0

        # 2. تلازم إيجابي قوي بين نمو الحجم والصعود
        if correlation > 0.3:
            smart_score += 30.0

        # 3. ثبات واستقرار السعر ضمن نطاق ضيق مع تصاعد الأحجام
        avg_vol_10 = volume.iloc[-10:-1].mean()
        avg_close_10 = close.iloc[-10:-1].mean()

        if avg_vol_10 > 0 and avg_close_10 > 0:
            if volume.iloc[-1] > (avg_vol_10 * 1.3):
                if (
                    (avg_close_10 * 0.98)
                    <= close.iloc[-1]
                    <= (avg_close_10 * 1.02)
                ):
                    smart_score += 20.0

        return float(min(100.0, max(0.0, smart_score)))

    def get_volume_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """إرجاع ناتج تحليل إشارات الحجم في صورة DataFrame موحد"""
        result = self.analyze(df)
        if 'error' in result:
            return pd.DataFrame()

        return pd.DataFrame([result])
