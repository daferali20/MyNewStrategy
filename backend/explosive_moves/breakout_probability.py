# backend/explosive_moves/breakout_probability.py
"""
حاسبة احتمالية الانفجار (Breakout Probability)
تحسب احتمالية اختراق السعر للحدود العلوية
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class BreakoutProbability:
    """
    حساب احتمالية الانفجار باستخدام عوامل متعددة
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.features = [
            'squeeze_score', 'volatility_score', 'compression_score',
            'volume_ratio', 'rsi', 'price_position'
        ]
    
    def calculate(self, df: pd.DataFrame, indicators: Dict = None) -> Dict:
        """
        حساب احتمالية الانفجار
        
        Args:
            df: DataFrame بالبيانات
            indicators: قاموس بالمؤشرات المحسوبة مسبقاً
        
        Returns:
            قاموس يحتوي على:
            - probability: float (0-100)
            - confidence: float (0-100)
            - factors: Dict
        """
        if df.empty or len(df) < 50:
            return {'error': 'بيانات غير كافية'}
        
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            # حساب المؤشرات
            if indicators is None:
                indicators = self._calculate_indicators(df)
            
            # عوامل الاحتمالية
            factors = self._calculate_factors(df, indicators)
            
            # حساب الاحتمالية الكلية
            probability = self._calculate_total_probability(factors)
            confidence = self._calculate_confidence(indicators)
            
            return {
                'probability': round(probability, 2),
                'confidence': round(confidence, 2),
                'factors': factors,
                'expected_move': round(factors.get('expected_move', 0), 2),
                'breakout_direction': 'up' if factors.get('direction_score', 0) > 0 else 'down'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """حساب المؤشرات الأساسية"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
        loss = loss.replace(0, np.nan)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # موقع السعر
        high_52 = high.iloc[-252:].max()
        price_position = (close.iloc[-1] / high_52) * 100 if high_52 > 0 else 50
        
        return {
            'rsi': rsi.iloc[-1] if not rsi.isna().iloc[-1] else 50,
            'price_position': price_position,
            'current_price': close.iloc[-1]
        }
    
    def _calculate_factors(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """حساب عوامل الاحتمالية"""
        close = df['Close']
        volume = df['Volume']
        
        # حجم التداول
        avg_volume = volume.iloc[-21:-1].mean()
        volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
        
        # المقاومة
        resistance = df['High'].iloc[-20:].max()
        current_price = close.iloc[-1]
        resistance_distance = (resistance - current_price) / current_price
        
        # التحرك المتوقع
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        expected_move = (atr / current_price) * 100
        
        # اتجاه الاحتمالية
        price_trend = close.iloc[-1] / close.iloc[-10:].mean()
        direction_score = 1 if price_trend > 1.02 else -1 if price_trend < 0.98 else 0
        
        return {
            'volume_ratio': round(volume_ratio, 2),
            'resistance_distance': round(resistance_distance * 100, 2),
            'expected_move': round(expected_move, 2),
            'direction_score': direction_score,
            'rsi_score': indicators.get('rsi', 50),
            'price_position': indicators.get('price_position', 50)
        }
    
    def _calculate_total_probability(self, factors: Dict) -> float:
        """حساب الاحتمالية الكلية"""
        # وزن كل عامل
        weights = {
            'volume_ratio': 0.25,
            'resistance_distance': 0.15,
            'expected_move': 0.20,
            'direction_score': 0.20,
            'rsi_score': 0.10,
            'price_position': 0.10
        }
        
        # تطبيع العوامل
        volume_score = min(100, factors['volume_ratio'] * 40)
        resistance_score = max(0, 100 - abs(factors['resistance_distance']) * 2)
        move_score = min(100, factors['expected_move'] * 10)
        direction_score = 50 + (factors['direction_score'] * 50)
        rsi_score = self._normalize_rsi(factors['rsi_score'])
        position_score = factors['price_position']
        
        # حساب المتوسط المرجح
        probability = (
            volume_score * weights['volume_ratio'] +
            resistance_score * weights['resistance_distance'] +
            move_score * weights['expected_move'] +
            direction_score * weights['direction_score'] +
            rsi_score * weights['rsi_score'] +
            position_score * weights['price_position']
        )
        
        return min(100, max(0, probability))
    
    def _normalize_rsi(self, rsi: float) -> float:
        """تطبيع قيمة RSI"""
        if 40 <= rsi <= 60:
            return 70
        elif 30 <= rsi <= 70:
            return 50
        else:
            return max(0, 100 - abs(rsi - 50) * 1.5)
    
    def _calculate_confidence(self, indicators: Dict) -> float:
        """حساب مستوى الثقة في الاحتمالية"""
        # عوامل الثقة
        rsi = indicators.get('rsi', 50)
        price_position = indicators.get('price_position', 50)
        
        # الثقة أعلى عندما تكون المؤشرات في نطاقات مثالية
        rsi_confidence = 100 - abs(rsi - 55) * 2
        position_confidence = 100 - abs(price_position - 80) * 1.5
        
        confidence = (rsi_confidence + position_confidence) / 2
        return min(100, max(0, confidence))
