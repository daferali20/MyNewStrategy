# backend/explosive_moves/ai_predictor.py
"""
متنبئ الذكاء الاصطناعي (AI Predictor)
يستخدم نماذج التعلم الآلي للتنبؤ بالحركات المتفجرة
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class AIPredictor:
    """
    التنبؤ بالحركات المتفجرة باستخدام الذكاء الاصطناعي
    """
    
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
        """تهيئة نموذج الذكاء الاصطناعي"""
        try:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                class_weight='balanced'
            )
            # تدريب مبدئي على بيانات محاكاة
            self._train_synthetic()
        except Exception as e:
            print(f"⚠️ خطأ في تهيئة النموذج: {e}")
            self.model = None
    
    def _train_synthetic(self):
        """تدريب النموذج على بيانات محاكاة"""
        np.random.seed(42)
        n_samples = 500
        
        X = np.random.randn(n_samples, len(self.features))
        y = np.zeros(n_samples)
        
        for i in range(n_samples):
            # احتمال الانفجار يزيد مع ارتفاع المؤشرات
            squeeze = X[i, 0] > 0.5
            volatility = X[i, 1] > 0.5
            volume = X[i, 3] > 0.6
            rsi = 0.3 < X[i, 4] < 0.7
            
            if squeeze and volatility and volume and rsi:
                y[i] = 1
            elif np.random.random() > 0.9:
                y[i] = 1
        
        self.model.fit(X, y)
        self.scaler.fit(X)
    
    def predict(self, indicators: Dict) -> Dict:
        """
        التنبؤ بالحركة المتفجرة
        
        Args:
            indicators: قاموس بالمؤشرات المحسوبة
        
        Returns:
            قاموس يحتوي على:
            - prediction: str (explosive/normal)
            - probability: float (0-100)
            - confidence: float (0-100)
            - expected_move_percent: float
            - time_horizon: str
        """
        if self.model is None:
            return self._fallback_prediction(indicators)
        
        try:
            # استخراج الميزات
            features = self._extract_features(indicators)
            
            if features is None:
                return self._fallback_prediction(indicators)
            
            # تطبيع الميزات
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # التنبؤ
            prob = self.model.predict_proba(features_scaled)[0]
            probability = prob[1] * 100
            
            # مستوى الثقة
            confidence = self._calculate_confidence(indicators)
            
            # التحرك المتوقع
            expected_move = self._calculate_expected_move(indicators)
            
            # الأفق الزمني
            time_horizon = self._estimate_time_horizon(indicators)
            
            return {
                'prediction': 'explosive' if probability > 60 else 'normal',
                'probability': round(probability, 2),
                'confidence': round(confidence, 2),
                'expected_move_percent': round(expected_move, 2),
                'time_horizon': time_horizon,
                'signal_strength': self._get_signal_strength(probability, confidence)
            }
            
        except Exception as e:
            return self._fallback_prediction(indicators)
    
    def _extract_features(self, indicators: Dict) -> Optional[np.ndarray]:
        """استخراج الميزات من المؤشرات"""
        try:
            features = [
                indicators.get('squeeze_score', 50),
                indicators.get('volatility_score', 50),
                indicators.get('compression_score', 50),
                indicators.get('volume_ratio', 1),
                indicators.get('rsi', 50),
                indicators.get('price_position', 50),
                indicators.get('smart_money_score', 50),
                indicators.get('call_put_ratio', 1),
                indicators.get('bb_width', 0.1),
                indicators.get('atr_ratio', 0.02)
            ]
            return np.array(features)
        except:
            return None
    
    def _calculate_confidence(self, indicators: Dict) -> float:
        """حساب مستوى الثقة"""
        # عوامل الثقة
        factors = [
            indicators.get('squeeze_score', 0),
            indicators.get('volume_ratio', 0) * 50,
            indicators.get('smart_money_score', 0)
        ]
        
        confidence = sum(factors) / len(factors)
        return min(100, max(0, confidence))
    
    def _calculate_expected_move(self, indicators: Dict) -> float:
        """حساب التحرك المتوقع"""
        # تقدير بناءً على ATR والمؤشرات
        atr_ratio = indicators.get('atr_ratio', 0.02)
        squeeze_score = indicators.get('squeeze_score', 50)
        
        base_move = atr_ratio * 100
        multiplier = 1 + (squeeze_score / 100)
        
        return base_move * multiplier
    
    def _estimate_time_horizon(self, indicators: Dict) -> str:
        """تقدير الأفق الزمني للانفجار"""
        squeeze_score = indicators.get('squeeze_score', 50)
        compression_days = indicators.get('compression_days', 0)
        
        if squeeze_score > 80 and compression_days > 5:
            return "فوري (خلال ساعات)"
        elif squeeze_score > 70 or compression_days > 10:
            return "قصير المدى (خلال أيام)"
        elif squeeze_score > 50:
            return "متوسط المدى (خلال أسبوع)"
        else:
            return "طويل المدى (أسبوع+)"
    
    def _get_signal_strength(self, probability: float, confidence: float) -> str:
        """تحديد قوة الإشارة"""
        avg = (probability + confidence) / 2
        
        if avg > 80:
            return "قوي جداً 🔥"
        elif avg > 65:
            return "قوي 💪"
        elif avg > 50:
            return "متوسط 📊"
        else:
            return "ضعيف ⚠️"
    
    def _fallback_prediction(self, indicators: Dict) -> Dict:
        """تنبؤ احتياطي في حالة فشل النموذج"""
        # تقدير بسيط باستخدام المؤشرات
        squeeze = indicators.get('squeeze_score', 0)
        volume = indicators.get('volume_ratio', 1)
        
        probability = min(100, (squeeze * 0.6 + volume * 20))
        confidence = min(100, (squeeze * 0.4 + 30))
        
        return {
            'prediction': 'explosive' if probability > 60 else 'normal',
            'probability': round(probability, 2),
            'confidence': round(confidence, 2),
            'expected_move_percent': round(indicators.get('atr_ratio', 0.02) * 100 * 2, 2),
            'time_horizon': self._estimate_time_horizon(indicators),
            'signal_strength': 'متوسط 📊' if probability > 50 else 'ضعيف ⚠️'
        }
