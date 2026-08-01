# backend/explosive_moves/ai_predictor.py
"""
متنبئ الذكاء الاصطناعي (AI Predictor Module)
يستخدم نماذج التعلم الآلي (Random Forest) لتوقع الانفجارات السعرية الوشيكة
بناءً على تجميع مؤشرات الضغط والسيولة والتذبذب.
"""

from typing import Dict, List, Tuple, Optional, Any
import warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')


class AIPredictor:
    """التنبؤ بالحركات المتفجرة باستخدام الذكاء الاصطناعي"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.features = [
            'squeeze_score', 'volatility_score', 'compression_score',
            'volume_ratio', 'rsi', 'price_position', 'smart_money_score',
            'call_put_ratio', 'bb_width', 'atr_ratio'
        ]
        self._init_model()

    def _init_model(self):
        """تهيئة وتدريب نموذج الذكاء الاصطناعي مبدئياً"""
        try:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                min_samples_split=4,
                random_state=42,
                class_weight='balanced'
            )
            # تدريب مبدئي على بيانات محاكاة تتوافق مع النطاقات الواقعية
            self._train_synthetic()
        except Exception as e:
            print(f"⚠️ خطأ في تهيئة نموذج الذكاء الاصطناعي: {e}")
            self.model = None

    def _train_synthetic(self):
        """تدريب النموذج على بيانات محاكاة منطقية تطابق المقاييس الواقعية"""
        np.random.seed(42)
        n_samples = 600

        # توليد قيم مطابقة واقعياً للميزات
        squeeze_score = np.random.uniform(0, 100, n_samples)
        volatility_score = np.random.uniform(0, 100, n_samples)
        compression_score = np.random.uniform(0, 100, n_samples)
        volume_ratio = np.random.uniform(0.5, 4.0, n_samples)
        rsi = np.random.uniform(20, 80, n_samples)
        price_position = np.random.uniform(0, 100, n_samples)
        smart_money_score = np.random.uniform(0, 100, n_samples)
        call_put_ratio = np.random.uniform(0.5, 3.0, n_samples)
        bb_width = np.random.uniform(0.01, 0.2, n_samples)
        atr_ratio = np.random.uniform(0.01, 0.08, n_samples)

        X = np.column_stack([
            squeeze_score, volatility_score, compression_score,
            volume_ratio, rsi, price_position, smart_money_score,
            call_put_ratio, bb_width, atr_ratio
        ])

        y = np.zeros(n_samples)
        for i in range(n_samples):
            # يرتفع احتمال الانفجار عند تلاقٍ مرتفع في النطاق والضغط والسيولة
            is_high_squeeze = X[i, 0] > 65
            is_compressed = X[i, 2] > 60
            is_high_volume = X[i, 3] > 1.5
            is_smart_flow = X[i, 6] > 60

            if is_high_squeeze and is_compressed and (is_high_volume or is_smart_flow):
                y[i] = 1
            elif np.random.random() < 0.08:  # ضوضاء عشوائية بسيطة للتوازن
                y[i] = 1

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        التنبؤ بالحركة المتفجرة عبر نموذج الذكاء الاصطناعي

        Args:
            indicators: قاموس المؤشرات المحسوبة

        Returns:
            Dict يحتوي على نتيجة التنبؤ، الاحتمالية، الثقة والأفق الزمني
        """
        if self.model is None:
            return self._fallback_prediction(indicators)

        try:
            features = self._extract_features(indicators)

            if features is None:
                return self._fallback_prediction(indicators)

            # تطبيع البيانات
            features_scaled = self.scaler.transform(features.reshape(1, -1))

            # حساب الاحتمالية
            prob = self.model.predict_proba(features_scaled)[0]
            probability = float(prob[1] * 100.0)

            # حساب الثقة والتحرك المتوقع
            confidence = float(self._calculate_confidence(indicators))
            expected_move = float(self._calculate_expected_move(indicators))
            time_horizon = self._estimate_time_horizon(indicators)

            return {
                'prediction': 'explosive' if probability > 60.0 else 'normal',
                'probability': round(probability, 2),
                'confidence': round(confidence, 2),
                'expected_move_percent': round(expected_move, 2),
                'time_horizon': time_horizon,
                'signal_strength': self._get_signal_strength(probability, confidence)
            }

        except Exception:
            return self._fallback_prediction(indicators)

    def _extract_features(self, indicators: Dict[str, Any]) -> Optional[np.ndarray]:
        """استخراج الميزات وضمان تسلسلها الصحيح"""
        try:
            features = [
                float(indicators.get('squeeze_score', 50.0)),
                float(indicators.get('volatility_score', 50.0)),
                float(indicators.get('compression_score', 50.0)),
                float(indicators.get('volume_ratio', 1.0)),
                float(indicators.get('rsi', 50.0)),
                float(indicators.get('price_position', 50.0)),
                float(indicators.get('smart_money_score', 50.0)),
                float(indicators.get('call_put_ratio', 1.0)),
                float(indicators.get('bb_width', 0.05)),
                float(indicators.get('atr_ratio', 0.02))
            ]
            return np.array(features)
        except Exception:
            return None

    def _calculate_confidence(self, indicators: Dict[str, Any]) -> float:
        """حساب درجة الثقة بناءً على اتساق المؤشرات"""
        squeeze = float(indicators.get('squeeze_score', 0.0))
        volume_norm = float(indicators.get('volume_ratio', 1.0)) * 25.0
        smart_money = float(indicators.get('smart_money_score', 0.0))
        compression = float(indicators.get('compression_score', 0.0))

        confidence = (squeeze * 0.35) + (min(100.0, volume_norm) * 0.25) + (smart_money * 0.2) + (compression * 0.2)
        return float(np.clip(confidence, 10.0, 100.0))

    def _calculate_expected_move(self, indicators: Dict[str, Any]) -> float:
        """تقدير نسبة التغير المئوي المتوقعة"""
        atr_ratio = float(indicators.get('atr_ratio', 0.02))
        squeeze_score = float(indicators.get('squeeze_score', 50.0))

        base_move = atr_ratio * 100.0
        multiplier = 1.0 + (squeeze_score / 50.0)

        return float(base_move * multiplier)

    def _estimate_time_horizon(self, indicators: Dict[str, Any]) -> str:
        """تقدير الفترة الزمنية لتحقق الانفجار"""
        squeeze_score = float(indicators.get('squeeze_score', 50.0))
        compression_days = int(indicators.get('compression_days', 0))

        if squeeze_score > 80 and compression_days >= 5:
            return "فوري (خلال ساعات / 1-2 يوم)"
        elif squeeze_score > 65 or compression_days > 7:
            return "قصير المدى (خلال 3-5 أيام)"
        elif squeeze_score > 45:
            return "متوسط المدى (خلال أسبوع)"
        else:
            return "طويل المدى (أسبوعين+)"

    def _get_signal_strength(self, probability: float, confidence: float) -> str:
        """تحديد القوة الإجمالية للإشارة"""
        avg_score = (probability * 0.6) + (confidence * 0.4)

        if avg_score >= 75.0:
            return "قوي جداً 🔥"
        elif avg_score >= 60.0:
            return "قوي 💪"
        elif avg_score >= 45.0:
            return "متوسط 📊"
        else:
            return "ضعيف ⚠️"

    def _fallback_prediction(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """طريقة التنبؤ الاحتياطية في حال تعذر تشغيل النموذج"""
        squeeze = float(indicators.get('squeeze_score', 0.0))
        volume = float(indicators.get('volume_ratio', 1.0))
        compression = float(indicators.get('compression_score', 0.0))

        probability = float(np.clip((squeeze * 0.5) + (compression * 0.3) + (volume * 15.0), 0.0, 100.0))
        confidence = float(np.clip((squeeze * 0.4) + 30.0, 10.0, 100.0))

        return {
            'prediction': 'explosive' if probability > 60.0 else 'normal',
            'probability': round(probability, 2),
            'confidence': round(confidence, 2),
            'expected_move_percent': round(float(indicators.get('atr_ratio', 0.02) * 200.0), 2),
            'time_horizon': self._estimate_time_horizon(indicators),
            'signal_strength': self._get_signal_strength(probability, confidence)
        }
