# backend/explosive_moves/score.py
"""
نظام التقييم المتكامل (Score System Module)
يجمع جميع مؤشرات الانفجار السعري ويحسب الدرجة النهائية ونسب الثقة والمخاطرة
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd


@dataclass
class ExplosiveScore:
    """درجة الانفجار المتكاملة - تجمع كافة المؤشرات والتحليلات المتقدمة"""

    # الدرجات الأساسية
    squeeze_score: float = 0.0
    volatility_score: float = 0.0
    compression_score: float = 0.0
    breakout_probability: float = 0.0
    volume_score: float = 0.0
    smart_money_score: float = 0.0
    options_score: float = 50.0
    ai_score: float = 50.0

    # الدرجة النهائية والثقة
    total_score: float = 0.0
    confidence: float = 0.0

    # التصنيفات الإشارية
    rating: str = "ضعيف ⚠️"
    signal: str = "تجنب 🔴"
    risk_level: str = "مرتفع ❌"

    # تفاصيل إضافية
    details: Dict = field(default_factory=dict)
    timestamp: str = ""

    def _safe_get_float(self, val: Union[float, int, None], default: float = 0.0) -> float:
        """تحويل القيمة بأمان إلى float وتجنب NaN/Inf"""
        if val is None:
            return default
        try:
            f_val = float(val)
            return f_val if not np.isnan(f_val) and not np.isinf(f_val) else default
        except (ValueError, TypeError):
            return default

    def calculate(self, indicators: Dict) -> 'ExplosiveScore':
        """حساب الدرجة النهائية من القاموس المجمع للمؤشرات

        Args:
            indicators: قاموس يحتوي على مخرجات التحليلات المختلفة

        Returns:
            ExplosiveScore الكائن المحدث
        """
        if not indicators or not isinstance(indicators, dict):
            indicators = {}

        # استخراج وتنقيتها كـ floats
        self.squeeze_score = self._safe_get_float(indicators.get('squeeze_score'))
        self.volatility_score = self._safe_get_float(indicators.get('volatility_score'))
        self.compression_score = self._safe_get_float(indicators.get('compression_score'))
        self.breakout_probability = self._safe_get_float(indicators.get('breakout_probability'))
        self.volume_score = self._safe_get_float(
            indicators.get('volume_score', indicators.get('surge_strength', 0))
        )
        self.smart_money_score = self._safe_get_float(indicators.get('smart_money_score'))
        self.options_score = self._safe_get_float(indicators.get('options_score'), default=50.0)
        self.ai_score = self._safe_get_float(
            indicators.get('ai_score', indicators.get('ai_probability', 50.0)), default=50.0
        )

        # أوزان المؤشرات المرجحة (Weights)
        weights = {
            'squeeze': 0.25,
            'volatility': 0.10,
            'compression': 0.15,
            'breakout': 0.20,
            'volume': 0.10,
            'smart_money': 0.10,
            'options': 0.05,
            'ai': 0.05,
        }

        # حساب الدرجة المرجحة المجمعة
        weighted_total = (
            self.squeeze_score * weights['squeeze']
            + self.volatility_score * weights['volatility']
            + self.compression_score * weights['compression']
            + self.breakout_probability * weights['breakout']
            + self.volume_score * weights['volume']
            + self.smart_money_score * weights['smart_money']
            + self.options_score * weights['options']
            + self.ai_score * weights['ai']
        )

        self.total_score = float(np.clip(weighted_total, 0.0, 100.0))

        # حساب الثقة والتقييمات
        self.confidence = self._calculate_confidence(indicators)
        self.rating = self._get_rating()
        self.signal = self._get_signal()
        self.risk_level = self._get_risk_level()

        self.details = indicators
        self.timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

        return self

    def _calculate_confidence(self, indicators: Dict) -> float:
        """حساب درجة الثقة بناءً على جودة واتساق البيانات"""
        core_keys = [
            'squeeze_score',
            'volatility_score',
            'compression_score',
            'breakout_probability',
            'volume_score',
            'smart_money_score',
        ]

        present_keys = sum(1 for k in core_keys if k in indicators and indicators[k] is not None)
        diversity_score = (present_keys / len(core_keys)) * 100.0

        # اتساق المؤشرات الفنية
        consistency = self._check_consistency()

        conf = (diversity_score * 0.6) + (consistency * 0.4)
        return float(np.clip(conf, 0.0, 100.0))

    def _check_consistency(self) -> float:
        """قياس مدى الاتساق والتناغم بين أبعاد المؤشرات الفنية المختلفة"""
        scores = [
            self.squeeze_score,
            self.volatility_score,
            self.compression_score,
            self.breakout_probability,
        ]

        # تصفية القيم غير الصفرية
        valid_scores = [s for s in scores if s > 0]
        if len(valid_scores) < 2:
            return 50.0

        std = float(np.std(valid_scores))

        if std < 5.0:
            return 90.0
        elif std < 10.0:
            return 75.0
        elif std < 20.0:
            return 50.0
        else:
            return 30.0

    def _get_rating(self) -> str:
        """تحديد التصنيف النصي العام"""
        if self.total_score >= 80:
            return "ممتاز 🌟"
        elif self.total_score >= 65:
            return "جيد جداً 📈"
        elif self.total_score >= 50:
            return "جيد ✅"
        elif self.total_score >= 35:
            return "متوسط 📊"
        else:
            return "ضعيف ⚠️"

    def _get_signal(self) -> str:
        """تحديد الإشارة الشرائية/التحذيرية"""
        if self.total_score >= 70 and self.confidence >= 60:
            return "شراء قوي 🟢"
        elif self.total_score >= 55 and self.confidence >= 50:
            return "شراء 🟡"
        elif self.total_score >= 40:
            return "مراقبة 🔍"
        else:
            return "تجنب 🔴"

    def _get_risk_level(self) -> str:
        """تحديد مستوى مخاطرة الصفقة"""
        if self.total_score >= 70:
            return "منخفض ✅"
        elif self.total_score >= 50:
            return "متوسط ⚠️"
        else:
            return "مرتفع ❌"

    def to_dict(self) -> Dict:
        """تحويل الكائن إلى قاموس تفصيلي مجمع"""
        return {
            'total_score': round(float(self.total_score), 2),
            'confidence': round(float(self.confidence), 2),
            'rating': self.rating,
            'signal': self.signal,
            'risk_level': self.risk_level,
            'squeeze_score': round(float(self.squeeze_score), 2),
            'volatility_score': round(float(self.volatility_score), 2),
            'compression_score': round(float(self.compression_score), 2),
            'breakout_probability': round(float(self.breakout_probability), 2),
            'volume_score': round(float(self.volume_score), 2),
            'smart_money_score': round(float(self.smart_money_score), 2),
            'options_score': round(float(self.options_score), 2),
            'ai_score': round(float(self.ai_score), 2),
            'timestamp': self.timestamp,
            'details': self.details,
        }

    def to_dataframe(self) -> pd.DataFrame:
        """تحويل المخرجات إلى Dataframe موحد"""
        return pd.DataFrame([self.to_dict()])

    def summary(self) -> str:
        """ملخص نصي متكامل للعرض المباشر"""
        return f"""
📊 **ملخص تحليل الانفجار السعري**
{'='*40}

🎯 الدرجة النهائية: {self.total_score:.1f}/100
📈 الثقة: {self.confidence:.1f}%
⭐ التصنيف: {self.rating}
💡 الإشارة: {self.signal}
🛡️ المخاطرة: {self.risk_level}

📌 تفاصيل المؤشرات:
• درجة الانضغاط (Squeeze): {self.squeeze_score:.1f}
• درجة التقلبات (Volatility): {self.volatility_score:.1f}
• درجة الانضغاط السعري (Compression): {self.compression_score:.1f}
• احتمالية الاختراق (Breakout): {self.breakout_probability:.1f}
• درجة الحجم (Volume): {self.volume_score:.1f}
• السيولة الذكية (Smart Money): {self.smart_money_score:.1f}

⏱️ التوقيت: {self.timestamp}
"""
