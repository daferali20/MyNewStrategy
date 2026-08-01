# backend/explosive_moves/volatility.py
"""
محلل التقلبات السعرية (Volatility Analyzer Module)
يحلل ATR والتقلبات التاريخية وعرض نطاقات بولينجر للتنبؤ بالانفجارات السعرية
"""

from typing import Dict, Union
import numpy as np
import pandas as pd


class VolatilityAnalyzer:
    """تحليل التقلبات السعرية باستخدام ATR، Bollinger Bands، والتقلبات التاريخية"""

    def __init__(self, atr_period: int = 14, lookback: int = 20):
        self.atr_period = atr_period
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

    def analyze(self, df: pd.DataFrame) -> Dict[str, Union[float, bool, str]]:
        """تحليل التقلبات السعرية وإرجاع مؤشرات الجاهزية الانفجارية

        Returns:
            Dict يحتوي على مقاييس ATR والتقلب التاريخي وعرض بولينجر
        """
        if df is None or df.empty or len(df) < max(self.lookback, self.atr_period):
            return {'error': 'بيانات غير كافية لتحليل التقلبات'}

        try:
            high = self._get_column(df, 'high')
            low = self._get_column(df, 'low')
            close = self._get_column(df, 'close')

            if high.empty or low.empty or close.empty:
                return {'error': 'أعمدة الأسعار (high/low/close) غير متوفرة بالكامل'}

            # 1. حساب متوسط النطاق الحقيقي (ATR)
            high_low = high - low
            high_close = (high - close.shift()).abs()
            low_close = (low - close.shift()).abs()

            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(self.atr_period, min_periods=1).mean()

            current_atr = float(atr.iloc[-1])
            current_price = float(close.iloc[-1])

            if current_price <= 0:
                return {'error': 'السعر الحالي غير صحيح'}

            atr_percent = (current_atr / current_price) * 100.0

            # 2. حساب التقلبات التاريخية المئوية (Historical Volatility - Annualized)
            returns = close.pct_change().dropna()
            if len(returns) >= self.lookback:
                historical_vol = returns.rolling(self.lookback).std() * np.sqrt(252) * 100.0
                current_hist_vol = float(np.nan_to_num(historical_vol.iloc[-1], nan=0.0))
            else:
                current_hist_vol = 0.0

            # 3. متوسط التقلبات ونسبة التوسع
            avg_atr = float(atr.iloc[-self.lookback : -1].mean())
            if pd.isna(avg_atr) or avg_atr <= 0:
                avg_atr = current_atr if current_atr > 0 else 1.0

            volatility_ratio = current_atr / avg_atr
            volatility_ratio = (
                float(np.nan_to_num(volatility_ratio, nan=1.0, posinf=1.0))
                if not np.isinf(volatility_ratio)
                else 3.0
            )

            # 4. تحديد انفجار التقلبات
            volatility_breakout = bool(volatility_ratio > 1.5)

            # 5. حساب درجة التقلبات (Volatility Score 0-100)
            if volatility_ratio > 2.0:
                vol_score = 90.0 + min(10.0, (volatility_ratio - 2.0) * 10.0)
            elif volatility_ratio > 1.5:
                vol_score = 70.0 + (volatility_ratio - 1.5) * 40.0
            elif volatility_ratio > 1.0:
                vol_score = 50.0 + (volatility_ratio - 1.0) * 40.0
            else:
                vol_score = max(0.0, 50.0 - (1.0 - volatility_ratio) * 50.0)

            vol_score = float(min(100.0, max(0.0, vol_score)))

            # 6. حساب Bollinger Bands Width
            bb_middle = close.rolling(20, min_periods=1).mean()
            bb_std = close.rolling(20, min_periods=1).std().fillna(0)
            bb_upper = bb_middle + (bb_std * 2.0)
            bb_lower = bb_middle - (bb_std * 2.0)

            bb_middle_val = float(bb_middle.iloc[-1])
            if bb_middle_val > 0:
                bb_width_val = float((bb_upper.iloc[-1] - bb_lower.iloc[-1]) / bb_middle_val)
            else:
                bb_width_val = 0.0

            return {
                'current_atr': round(current_atr, 2),
                'atr_percent': round(atr_percent, 2),
                'volatility_ratio': round(volatility_ratio, 2),
                'historical_volatility': round(current_hist_vol, 2),
                'volatility_breakout': volatility_breakout,
                'volatility_score': round(vol_score, 2),
                'bb_width': round(bb_width_val, 4),
                'current_price': round(current_price, 2),
            }

        except Exception as e:
            return {'error': f'حدث خطأ أثناء تحليل التقلبات: {str(e)}'}

    def get_volatility_breakouts(self, df: pd.DataFrame, threshold: float = 1.5) -> pd.DataFrame:
        """الحصول على ناتج تحليل نقاط الانفجار في صورة DataFrame موحد"""
        result = self.analyze(df)
        if 'error' in result:
            return pd.DataFrame()

        return pd.DataFrame([result])
