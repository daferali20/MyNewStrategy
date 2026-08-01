# backend/explosive_moves/breakout_probability.py
"""
حاسبة احتمالية الانفجار والاختراق (Breakout Probability Calculator)
تقوم بحساب وتوقع احتمالية الاختراق السعري بناءً على العوامل الفنية، 
حجم التداول، ونسبة الانضغاط.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class BreakoutProbability:
    """حساب احتمالية الانفجار والاتجاه المتوقع باستخدام مؤشرات متعددة"""

    def __init__(self):
        self.features = [
            'squeeze_score', 'volatility_score', 'compression_score',
            'volume_ratio', 'rsi', 'price_position'
        ]

    def calculate(self, df: pd.DataFrame, indicators: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        حساب احتمالية الاختراق ومستوى الثقة

        Args:
            df: DataFrame يحتوي على بيانات الأسعار (OHLCV)
            indicators: قاموس اختياري يحتوي على مؤشرات محسوبة مسبقاً (مثل squeeze_score)

        Returns:
            Dict يحتوي على الاحتمالية، درجة الثقة، العوامل، والاتجاه المتوقع
        """
        if df is None or df.empty or len(df) < 20:
            return {'error': 'بيانات غير كافية، يتطلب التحليل 20 شمعة على الأقل'}

        try:
            # 1. حساب المؤشرات الفنية الأساسية
            calculated_indicators = self._calculate_indicators(df)
            if indicators:
                calculated_indicators.update(indicators)

            # 2. حساب عوامل الاحتمالية
            factors = self._calculate_factors(df, calculated_indicators)

            # 3. حساب الاحتمالية الكلية ومستوى الثقة
            probability = self._calculate_total_probability(factors)
            confidence = self._calculate_confidence(calculated_indicators)

            direction_val = factors.get('direction_score', 0)
            breakout_dir = 'up' if direction_val > 0 else ('down' if direction_val < 0 else 'neutral')

            return {
                'probability': round(float(probability), 2),
                'confidence': round(float(confidence), 2),
                'factors': factors,
                'expected_move': round(float(factors.get('expected_move', 0.0)), 2),
                'breakout_direction': breakout_dir
            }

        except Exception as e:
            return {'error': f'حدث خطأ في حساب احتمالية الانفجار: {str(e)}'}

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """حساب RSI وموقع السعر النسبي باحتياط أمان"""
        close = df['Close']
        high = df['High']

        # 1. حساب RSI آمن (14 فترة)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0.0)).rolling(14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(14, min_periods=1).mean()

        rs = gain / loss.replace(0, np.nan)
        rsi_series = 100 - (100 / (1 + rs))
        rsi_val = rsi_series.iloc[-1]
        
        if pd.isna(rsi_val):
            rsi_val = 50.0

        # 2. موقع السعر بالنسبة لأعلى سعر (مرن بحسب البيانات المتاحة حتى 252 يوم)
        lookback_period = min(len(df), 252)
        high_period = float(high.iloc[-lookback_period:].max())
        current_price = float(close.iloc[-1])

        price_position = (current_price / high_period * 100.0) if high_period > 0 else 50.0

        return {
            'rsi': float(np.clip(rsi_val, 0.0, 100.0)),
            'price_position': float(np.clip(price_position, 0.0, 100.0)),
            'current_price': round(current_price, 2)
        }

    def _calculate_factors(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """حساب وتحليل العوامل المباشرة للاختراق"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume'] if 'Volume' in df.columns else pd.Series(1, index=df.index)

        current_price = float(close.iloc[-1])

        # 1. معدل حجم التداول (Volume Ratio)
        vol_period = min(len(df) - 1, 20)
        avg_volume = float(volume.iloc[-vol_period-1:-1].mean()) if vol_period > 0 else 1.0
        current_volume = float(volume.iloc[-1])
        volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1.0

        # 2. المسافة عن المقاومة القريبة
        res_period = min(len(df), 20)
        resistance = float(high.iloc[-res_period:].max())
        resistance_distance = ((resistance - current_price) / current_price * 100.0) if current_price > 0 else 0.0

        # 3. التحرك المتوقع (ATR %)
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
        atr = float(tr.rolling(14, min_periods=1).mean().iloc[-1])
        expected_move = (atr / current_price * 100.0) if current_price > 0 else 0.0

        # 4. اتجاه الحركة (Direction Score)
        trend_period = min(len(df), 10)
        recent_avg = float(close.iloc[-trend_period:].mean())
        price_trend = (current_price / recent_avg) if recent_avg > 0 else 1.0

        if price_trend > 1.015:
            direction_score = 1
        elif price_trend < 0.985:
            direction_score = -1
        else:
            direction_score = 0

        return {
            'volume_ratio': round(float(volume_ratio), 2),
            'resistance_distance': round(float(resistance_distance), 2),
            'expected_move': round(float(expected_move), 2),
            'direction_score': direction_score,
            'rsi_score': indicators.get('rsi', 50.0),
            'price_position': indicators.get('price_position', 50.0),
            'squeeze_score': indicators.get('squeeze_score', 0.0),
            'compression_score': indicators.get('compression_score', 0.0)
        }

    def _calculate_total_probability(self, factors: Dict[str, Any]) -> float:
        """حساب الاحتمالية الإجمالية للاختراق بالدرجات المرجحة"""
        weights = {
            'volume_ratio': 0.25,
            'resistance_distance': 0.15,
            'expected_move': 0.20,
            'direction_score': 0.15,
            'rsi_score': 0.10,
            'price_position': 0.15
        }

        # التطبيع والتقييم
        volume_score = min(100.0, factors.get('volume_ratio', 1.0) * 40.0)
        resistance_score = max(0.0, 100.0 - abs(factors.get('resistance_distance', 0.0)) * 5.0)
        move_score = min(100.0, factors.get('expected_move', 0.0) * 15.0)
        direction_score = 50.0 + (factors.get('direction_score', 0) * 40.0)
        rsi_score = self._normalize_rsi(factors.get('rsi_score', 50.0))
        position_score = factors.get('price_position', 50.0)

        # حساب المتوسط المرجح
        probability = (
            volume_score * weights['volume_ratio'] +
            resistance_score * weights['resistance_distance'] +
            move_score * weights['expected_move'] +
            direction_score * weights['direction_score'] +
            rsi_score * weights['rsi_score'] +
            position_score * weights['price_position']
        )

        # دمج تأثير الانضغاط إن وجد
        squeeze_score = factors.get('squeeze_score', 0.0)
        if squeeze_score > 0:
            probability = (probability * 0.7) + (squeeze_score * 0.3)

        return float(np.clip(probability, 0.0, 100.0))

    def _normalize_rsi(self, rsi: float) -> float:
        """تطبيع قيمة RSI لتحديد المناطق التجميعية والأكثر تفاؤلاً"""
        if 45.0 <= rsi <= 65.0:
            return 80.0
        elif 35.0 <= rsi <= 75.0:
            return 60.0
        else:
            return max(0.0, 100.0 - abs(rsi - 50.0) * 2.0)

    def _calculate_confidence(self, indicators: Dict[str, Any]) -> float:
        """حساب درجة الثقة بالاعتماد على الاتساق بين المؤشرات"""
        rsi = indicators.get('rsi', 50.0)
        price_position = indicators.get('price_position', 50.0)

        rsi_confidence = 100.0 - abs(rsi - 55.0) * 1.5
        position_confidence = 100.0 - abs(price_position - 75.0) * 1.2

        confidence = (rsi_confidence + position_confidence) / 2.0
        return float(np.clip(confidence, 10.0, 100.0))
