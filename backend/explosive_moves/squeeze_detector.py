# backend/explosive_moves/squeeze_detector.py
"""
كاشف الانضغاط السعري (Squeeze Detector Module)
يكتشف فترات انضغاط السعر (TTM Squeeze) التي تسبق الحركات والانفجارات السعرية
"""

from typing import Dict, List, Union
import numpy as np
import pandas as pd


class SqueezeDetector:
    """كشف انضغاط السعر المتقدم باستخدام Bollinger Bands و Keltner Channels"""

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        kc_period: int = 20,
        kc_atr_multiplier: float = 1.5,
    ):
        """
        Args:
            bb_period: فترة Bollinger Bands
            bb_std: عدد الانحرافات المعيارية
            kc_period: فترة Keltner Channels
            kc_atr_multiplier: مضاعف ATR لـ Keltner Channels
        """
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.kc_period = kc_period
        self.kc_atr_multiplier = kc_atr_multiplier

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

    def detect(self, df: pd.DataFrame) -> Dict[str, Union[float, bool, list, str]]:
        """كشف ومقياس الانضغاط السعري بالبيانات

        Returns:
            Dict يحتوي على درجة الانضغاط، نسبته، وحدود القنوات الفنية
        """
        min_required = max(self.bb_period, self.kc_period, 14)
        if df is None or df.empty or len(df) < min_required:
            return {'error': 'بيانات غير كافية لكشف الانضغاط السعري'}

        try:
            close = self._get_column(df, 'close')
            high = self._get_column(df, 'high')
            low = self._get_column(df, 'low')

            if close.empty or high.empty or low.empty:
                return {'error': 'أعمدة الأسعار (close, high, low) غير مكتملة'}

            # 1. حساب Bollinger Bands
            bb_middle = close.rolling(self.bb_period, min_periods=1).mean()
            bb_std_val = close.rolling(self.bb_period, min_periods=1).std().fillna(0)
            bb_upper = bb_middle + (bb_std_val * self.bb_std)
            bb_lower = bb_middle - (bb_std_val * self.bb_std)

            bb_middle_curr = float(bb_middle.iloc[-1])
            if bb_middle_curr > 0:
                bb_width = (bb_upper - bb_lower) / bb_middle
            else:
                bb_width = pd.Series(0.0, index=close.index)

            # 2. حساب Keltner Channels
            typical_price = (high + low + close) / 3.0
            kc_middle = typical_price.rolling(self.kc_period, min_periods=1).mean()

            # حساب ATR
            high_low = high - low
            high_close = (high - close.shift()).abs()
            low_close = (low - close.shift()).abs()
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(14, min_periods=1).mean()

            kc_upper = kc_middle + (atr * self.kc_atr_multiplier)
            kc_lower = kc_middle - (atr * self.kc_atr_multiplier)

            kc_middle_curr = float(kc_middle.iloc[-1])
            if kc_middle_curr > 0:
                kc_width = (kc_upper - kc_lower) / kc_middle
            else:
                kc_width = pd.Series(1.0, index=close.index)

            # 3. قياس القيم الحالية للـ Squeeze
            current_bb_width = float(np.nan_to_num(bb_width.iloc[-1], nan=0.0))
            current_kc_width = float(np.nan_to_num(kc_width.iloc[-1], nan=1.0))

            if current_kc_width > 0:
                ratio = current_bb_width / current_kc_width
            else:
                ratio = 1.0

            ratio = float(np.nan_to_num(ratio, nan=1.0, posinf=1.0))

            # 4. تاريخ الانضغاط الزمني (Squeeze History)
            squeeze_series = (bb_width < kc_width).astype(int)
            squeeze_history = squeeze_series.tail(50).tolist()

            # 5. حساب درجة الانضغاط (Squeeze Score 0-100)
            if ratio < 0.7:
                squeeze_score = 90.0 + (1.0 - ratio) * 33.0  # انضغاط شديد جداً
            elif ratio < 0.9:
                squeeze_score = 60.0 + (0.9 - ratio) * 200.0
            elif ratio < 1.1:
                squeeze_score = 40.0 + (1.1 - ratio) * 200.0
            else:
                squeeze_score = max(0.0, 40.0 - (ratio - 1.1) * 100.0)

            squeeze_score = float(min(100.0, max(0.0, squeeze_score)))

            # الحالة الحالية للانضغاط
            is_squeeze = bool(current_bb_width < current_kc_width)

            return {
                'is_squeeze': is_squeeze,
                'squeeze_score': round(squeeze_score, 2),
                'bb_width': round(current_bb_width, 4),
                'kc_width': round(current_kc_width, 4),
                'ratio': round(ratio, 3),
                'squeeze_history': squeeze_history,
                'bb_upper': round(float(bb_upper.iloc[-1]), 2),
                'bb_lower': round(float(bb_lower.iloc[-1]), 2),
                'kc_upper': round(float(kc_upper.iloc[-1]), 2),
                'kc_lower': round(float(kc_lower.iloc[-1]), 2),
            }

        except Exception as e:
            return {'error': f'حدث خطأ في كشف الانضغاط: {str(e)}'}

    def get_squeeze_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """إرجاع إشارات الانضغاط في صورة DataFrame موحد"""
        result = self.detect(df)
        if 'error' in result:
            return pd.DataFrame()

        return pd.DataFrame([
            {
                'squeeze_score': result['squeeze_score'],
                'is_squeeze': result['is_squeeze'],
                'bb_width': result['bb_width'],
                'kc_width': result['kc_width'],
                'ratio': result['ratio'],
            }
        ])
