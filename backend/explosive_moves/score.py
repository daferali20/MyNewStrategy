# backend/explosive_moves/score.py
"""
نظام التقييم المتكامل (Score System)
يجمع جميع المؤشرات ويعطي درجة نهائية للانفجار
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class ExplosiveScore:
    """
    درجة الانفجار المتكاملة - تجمع جميع المؤشرات
    """
    # الدرجات الأساسية
    squeeze_score: float = 0
    volatility_score: float = 0
    compression_score: float = 0
    breakout_probability: float = 0
    volume_score: float = 0
    smart_money_score: float = 0
    options_score: float = 0
    ai_score: float = 0
    
    # الدرجة النهائية
    total_score: float = 0
    confidence: float = 0
    
    # التصنيفات
    rating: str = "ضعيف"
    signal: str = "محايد"
    risk_level: str = "متوسط"
    
    # تفاصيل إضافية
    details: Dict = field(default_factory=dict)
    timestamp: str = ""
    
    def calculate(self, indicators: Dict) -> 'ExplosiveScore':
        """
        حساب الدرجة النهائية من المؤشرات
        
        Args:
            indicators: قاموس بجميع المؤشرات
        
        Returns:
            ExplosiveScore محدث
        """
        # استخراج الدرجات
        self.squeeze_score = indicators.get('squeeze_score', 0)
        self.volatility_score = indicators.get('volatility_score', 0)
        self.compression_score = indicators.get('compression_score', 0)
        self.breakout_probability = indicators.get('breakout_probability', 0)
        self.volume_score = indicators.get('surge_strength', 0)
        self.smart_money_score = indicators.get('smart_money_score', 0)
        self.options_score = indicators.get('options_score', 50)
        self.ai_score = indicators.get('ai_probability', 50)
        
        # حساب الدرجة النهائية (متوسط مرجح)
        weights = {
            'squeeze': 0.25,
            'volatility': 0.10,
            'compression': 0.15,
            'breakout': 0.20,
            'volume': 0.10,
            'smart_money': 0.10,
            'options': 0.05,
            'ai': 0.05
        }
        
        self.total_score = (
            self.squeeze_score * weights['squeeze'] +
            self.volatility_score * weights['volatility'] +
            self.compression_score * weights['compression'] +
            self.breakout_probability * weights['breakout'] +
            self.volume_score * weights['volume'] +
            self.smart_money_score * weights['smart_money'] +
            self.options_score * weights['options'] +
            self.ai_score * weights['ai']
        )
        
        # حساب الثقة
        self.confidence = self._calculate_confidence(indicators)
        
        # تحديد التصنيفات
        self.rating = self._get_rating()
        self.signal = self._get_signal()
        self.risk_level = self._get_risk_level()
        
        # تخزين التفاصيل
        self.details = indicators
        self.timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self
    
    def _calculate_confidence(self, indicators: Dict) -> float:
        """حساب مستوى الثقة"""
        # عدد المؤشرات المتاحة
        available = sum(1 for v in indicators.values() if v is not None and v > 0)
        total = len(indicators)
        
        if total == 0:
            return 0
        
        # تنوع المؤشرات يزيد الثقة
        diversity_score = (available / total) * 100
        
        # اتساق المؤشرات
        consistency = self._check_consistency(indicators)
        
        return min(100, (diversity_score * 0.6 + consistency * 0.4))
    
    def _check_consistency(self, indicators: Dict) -> float:
        """التحقق من اتساق المؤشرات"""
        scores = [
            indicators.get('squeeze_score', 0),
            indicators.get('volatility_score', 0),
            indicators.get('compression_score', 0),
            indicators.get('breakout_probability', 0)
        ]
        
        if not scores:
            return 50
        
        # حساب التباين
        mean = np.mean(scores)
        std = np.std(scores)
        
        # كلما قل التباين زاد الاتساق
        if std < 5:
            return 90
        elif std < 10:
            return 75
        elif std < 20:
            return 50
        else:
            return 30
    
    def _get_rating(self) -> str:
        """تحديد التصنيف"""
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
        """تحديد الإشارة"""
        if self.total_score >= 70 and self.confidence >= 60:
            return "شراء قوي 🟢"
        elif self.total_score >= 55 and self.confidence >= 50:
            return "شراء 🟡"
        elif self.total_score >= 40:
            return "مراقبة 🔍"
        else:
            return "تجنب 🔴"
    
    def _get_risk_level(self) -> str:
        """تحديد مستوى المخاطرة"""
        if self.total_score >= 70:
            return "منخفض ✅"
        elif self.total_score >= 50:
            return "متوسط ⚠️"
        else:
            return "مرتفع ❌"
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'total_score': round(self.total_score, 2),
            'confidence': round(self.confidence, 2),
            'rating': self.rating,
            'signal': self.signal,
            'risk_level': self.risk_level,
            'squeeze_score': round(self.squeeze_score, 2),
            'volatility_score': round(self.volatility_score, 2),
            'compression_score': round(self.compression_score, 2),
            'breakout_probability': round(self.breakout_probability, 2),
            'volume_score': round(self.volume_score, 2),
            'smart_money_score': round(self.smart_money_score, 2),
            'options_score': round(self.options_score, 2),
            'ai_score': round(self.ai_score, 2),
            'timestamp': self.timestamp,
            'details': self.details
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """تحويل إلى DataFrame"""
        return pd.DataFrame([self.to_dict()])
    
    def summary(self) -> str:
        """ملخص نصي"""
        return f"""
📊 **ملخص تحليل الانفجار**
{'='*40}

🎯 الدرجة النهائية: {self.total_score:.1f}/100
📈 الثقة: {self.confidence:.1f}%
⭐ التصنيف: {self.rating}
💡 الإشارة: {self.signal}
🛡️ المخاطرة: {self.risk_level}

📌 تفاصيل المؤشرات:
• درجة الانضغاط: {self.squeeze_score:.1f}
• درجة التقلبات: {self.volatility_score:.1f}
• درجة الانضغاط: {self.compression_score:.1f}
• احتمالية الانفجار: {self.breakout_probability:.1f}
• حجم التداول: {self.volume_score:.1f}
• السيولة الذكية: {self.smart_money_score:.1f}

⏱️ التوقيت: {self.timestamp}
"""
