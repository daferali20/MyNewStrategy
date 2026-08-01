# backend/explosive_moves/compression.py
"""
محلل الانضغاط السعري (Compression Analyzer Module)
يحلل فترات الضغط والتوافق السعري وتراجع التقلبات لتوقع الانفجارات السعرية الوشيكة.
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np


class CompressionAnalyzer:
    """تحليل الانضغاط السعري باستخدام نطاق التداول وأنماط تراجع التقلبات"""

    def __init__(self, lookback: int = 30, compression_threshold: float = 6.0):
        """
        Args:
            lookback: عدد الشموع السابقة للتحليل (افتراضي 30)
            compression_threshold: نسبة النطاق السعري المقبولة للانضغاط % (افتراضي 6.0%)
        """
        self.lookback = lookback
        self.compression_threshold = compression_threshold

    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        تحليل الانضغاط وتحديد قوته والنمط المكون

        Returns:
            قاموس يحتوي على نتائج الانضغاط وقوة الدرجة (0 - 100)
        """
        if df is None or df.empty or len(df) < self.lookback:
            return {'error': f'بيانات غير كافية، يتطلب التحليل {self.lookback} شمعة على الأقل'}

        try:
            high = df['High']
            low = df['Low']
            close = df['Close']
            volume = df['Volume'] if 'Volume' in df.columns else None

            # 1. حساب النطاق السعري الإجمالي في الفترة
            recent_high = float(high.iloc[-self.lookback:].max())
            recent_low = float(low.iloc[-self.lookback:].min())
            current_price = float(close.iloc[-1])

            if current_price <= 0:
                return {'error': 'سعر الإغلاق غير صالح'}

            price_range = recent_high - recent_low
            price_range_percent = (price_range / current_price) * 100.0

            # 2. كشف الانضغاط بناءً على النطاق الإجمالي
            is_compressed = bool(price_range_percent <= self.compression_threshold)

            # 3. حساب عدد أيام/شموع الانضغاط المتتالية مؤخراً
            compression_days = 0
            for i in range(len(df) - 1, len(df) - self.lookback - 1, -1):
                if i < 0:
                    break
                day_close = float(close.iloc[i])
                if day_close <= 0:
                    continue
                day_range = ((high.iloc[i] - low.iloc[i]) / day_close) * 100.0

                # يعتبر اليوم مضغوطاً إذا كان نطاقه أقل من نصف العتبة العامة
                if day_range <= (self.compression_threshold * 0.5):
                    compression_days += 1
                else:
                    break

            # 4. تحليل تراجع حجم التداول (Volume Decline)
            volume_decline = False
            if volume is not None and len(volume) >= self.lookback:
                avg_volume = float(volume.iloc[-self.lookback:-1].mean())
                current_volume = float(volume.iloc[-1])
                volume_decline = bool(current_volume < (avg_volume * 0.8))

            # 5. تحديد نمط الانضغاط
            pattern = self._identify_pattern(df)

            # 6. حساب درجة الانضغاط (Compression Score 0-100)
            if price_range_percent <= 0:
                range_score = 100.0
            else:
                range_score = max(0.0, 100.0 - (price_range_percent / self.compression_threshold) * 50.0)

            days_score = min(100.0, compression_days * 12.5)

            if is_compressed:
                compression_score = (days_score * 0.5) + (range_score * 0.5)
            else:
                compression_score = max(0.0, range_score * 0.6)

            compression_score = float(np.clip(compression_score, 0.0, 100.0))

            return {
                'is_compressed': is_compressed,
                'compression_score': round(compression_score, 2),
                'compression_days': int(compression_days),
                'price_range_percent': round(price_range_percent, 2),
                'volume_decline': volume_decline,
                'pattern': pattern,
                'recent_high': round(recent_high, 2),
                'recent_low': round(recent_low, 2),
                'current_price': round(current_price, 2)
            }

        except Exception as e:
            return {'error': f'حدث خطأ أثناء تحليل الانضغاط: {str(e)}'}

    def _identify_pattern(self, df: pd.DataFrame) -> str:
        """تحديد اتجاه وشكل نمط الانضغاط"""
        close = df['Close']
        current_price = float(close.iloc[-1])

        # حساب الاتجاه مرناً بحسب البيانات المتاحة (استخدام 50 أو المتاح)
        sma_period = min(len(df), 50)
        sma_val = float(close.rolling(sma_period).mean().iloc[-1])

        if current_price > sma_val * 1.01:
            direction = "صاعد"
        elif current_price < sma_val * 0.99:
            direction = "هابط"
        else:
            direction = "جانبي"

        # تحديد النمط بناءً على تضييق النطاقات الأخيرة
        recent_10_range = (df['High'].iloc[-10:] - df['Low'].iloc[-10:]).mean()
        older_10_range = (df['High'].iloc[-20:-10] - df['Low'].iloc[-20:-10]).mean() if len(df) >= 20 else recent_10_range

        if older_10_range > 0 and (recent_10_range / older_10_range) < 0.6:
            shape = "مثلث مضيق 📐"
        elif recent_10_range < (current_price * 0.02):
            shape = "قناة ضيقة 📈"
        else:
            shape = "انضغاط عادي 📊"

        return f"{direction} - {shape}"

    def get_compression_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """إرجاع ملخص إشارات الانضغاط كـ DataFrame"""
        result = self.analyze(df)
        if 'error' in result:
            return pd.DataFrame()

        return pd.DataFrame([{
            'compression_score': result['compression_score'],
            'is_compressed': result['is_compressed'],
            'compression_days': result['compression_days'],
            'price_range_percent': result['price_range_percent'],
            'volume_decline': result['volume_decline'],
            'pattern': result['pattern']
        }])
