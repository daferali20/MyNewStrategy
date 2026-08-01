# backend/explosive_moves/integration.py
"""
دمج جميع مكونات الحركات المتفجرة في نظام واحد
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from .squeeze_detector import SqueezeDetector
from .volatility import VolatilityAnalyzer
from .compression import CompressionAnalyzer
from .breakout_probability import BreakoutProbability
from .volume_expansion import VolumeExpansion
from .smart_money import SmartMoneyAnalyzer
from .options_flow import OptionsFlowAnalyzer
from .ai_predictor import AIPredictor
from .score import ExplosiveScore

class ExplosiveMovesAnalyzer:
    """
    المحلل المتكامل للحركات المتفجرة
    يدمج جميع المكونات في تحليل واحد شامل
    """
    
    def __init__(self):
        self.squeeze = SqueezeDetector()
        self.volatility = VolatilityAnalyzer()
        self.compression = CompressionAnalyzer()
        self.breakout = BreakoutProbability()
        self.volume = VolumeExpansion()
        self.smart_money = SmartMoneyAnalyzer()
        self.options = OptionsFlowAnalyzer()
        self.ai = AIPredictor()
        self.score = ExplosiveScore()
    
    def analyze(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> Dict:
        """
        تحليل شامل للحركات المتفجرة
        
        Args:
            df: DataFrame بالبيانات
            symbol: رمز السهم
        
        Returns:
            قاموس بالنتائج الكاملة
        """
        if df.empty or len(df) < 50:
            return {'error': 'بيانات غير كافية'}
        
        try:
            # جمع جميع المؤشرات
            indicators = self._collect_indicators(df, symbol)
            
            # حساب الدرجة النهائية
            score_result = self.score.calculate(indicators)
            
            # تجميع النتائج
            return {
                'symbol': symbol,
                'timestamp': pd.Timestamp.now().isoformat(),
                'score': score_result.to_dict(),
                'indicators': indicators,
                'summary': score_result.summary(),
                'recommendation': self._get_recommendation(score_result)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _collect_indicators(self, df: pd.DataFrame, symbol: str) -> Dict:
        """جمع جميع المؤشرات"""
        indicators = {}
        
        # 1. كشف الانضغاط
        squeeze_result = self.squeeze.detect(df)
        if 'error' not in squeeze_result:
            indicators.update({
                'squeeze_score': squeeze_result.get('squeeze_score', 0),
                'is_squeeze': squeeze_result.get('is_squeeze', False),
                'bb_width': squeeze_result.get('bb_width', 0),
                'kc_width': squeeze_result.get('kc_width', 0)
            })
        
        # 2. تحليل التقلبات
        volatility_result = self.volatility.analyze(df)
        if 'error' not in volatility_result:
            indicators.update({
                'volatility_score': volatility_result.get('volatility_score', 0),
                'volatility_ratio': volatility_result.get('volatility_ratio', 1),
                'atr_ratio': volatility_result.get('atr_percent', 0) / 100
            })
        
        # 3. تحليل الانضغاط
        compression_result = self.compression.analyze(df)
        if 'error' not in compression_result:
            indicators.update({
                'compression_score': compression_result.get('compression_score', 0),
                'compression_days': compression_result.get('compression_days', 0),
                'is_compressed': compression_result.get('is_compressed', False)
            })
        
        # 4. احتمالية الانفجار
        breakout_result = self.breakout.calculate(df, indicators)
        if 'error' not in breakout_result:
            indicators.update({
                'breakout_probability': breakout_result.get('probability', 0),
                'breakout_confidence': breakout_result.get('confidence', 0),
                'expected_move': breakout_result.get('expected_move', 0)
            })
        
        # 5. حجم التداول
        volume_result = self.volume.analyze(df)
        if 'error' not in volume_result:
            indicators.update({
                'volume_ratio': volume_result.get('volume_ratio', 1),
                'surge_strength': volume_result.get('surge_strength', 0),
                'is_surge': volume_result.get('is_surge', False),
                'is_smart_money': volume_result.get('is_smart_money', False)
            })
        
        # 6. السيولة الذكية
        smart_result = self.smart_money.analyze(df)
        if 'error' not in smart_result:
            indicators.update({
                'smart_money_score': smart_result.get('smart_money_score', 50),
                'accumulation': smart_result.get('accumulation', False),
                'distribution': smart_result.get('distribution', False),
                'buy_pressure': smart_result.get('buy_pressure', 50),
                'sell_pressure': smart_result.get('sell_pressure', 50)
            })
        
        # 7. الخيارات (محاكاة)
        options_result = self.options.analyze(symbol)
        if 'error' not in options_result:
            indicators.update({
                'options_score': options_result.get('smart_money_score', 50),
                'call_put_ratio': options_result.get('call_put_ratio', 1),
                'sentiment': options_result.get('sentiment', 'محايد')
            })
        
        # 8. الذكاء الاصطناعي
        ai_result = self.ai.predict(indicators)
        if 'error' not in ai_result:
            indicators.update({
                'ai_probability': ai_result.get('probability', 50),
                'ai_confidence': ai_result.get('confidence', 50),
                'ai_prediction': ai_result.get('prediction', 'normal'),
                'expected_move_percent': ai_result.get('expected_move_percent', 0)
            })
        
        # 9. مؤشرات إضافية من البيانات
        indicators.update(self._get_basic_indicators(df))
        
        return indicators
    
    def _get_basic_indicators(self, df: pd.DataFrame) -> Dict:
        """استخراج مؤشرات أساسية من البيانات"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
        loss = loss.replace(0, np.nan)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # موقع السعر
        high_52 = high.iloc[-252:].max()
        price_position = (close.iloc[-1] / high_52 * 100) if high_52 > 0 else 50
        
        return {
            'rsi': rsi.iloc[-1] if not rsi.isna().iloc[-1] else 50,
            'price_position': price_position,
            'current_price': close.iloc[-1],
            'high_52': high_52,
            'low_52': low.iloc[-252:].min() if len(low) > 252 else low.min()
        }
    
    def _get_recommendation(self, score: ExplosiveScore) -> Dict:
        """توليد توصية بناءً على الدرجة"""
        total = score.total_score
        confidence = score.confidence
        
        if total >= 70 and confidence >= 60:
            action = "شراء قوي 🟢"
            details = "جميع المؤشرات تشير إلى انفجار سعري وشيك"
        elif total >= 55 and confidence >= 50:
            action = "شراء 🟡"
            details = "مؤشرات إيجابية مع وجود بعض المخاطر"
        elif total >= 40:
            action = "مراقبة 🔍"
            details = "مؤشرات محايدة، انتظر تأكيد"
        else:
            action = "تجنب 🔴"
            details = "مؤشرات سلبية، خطر مرتفع"
        
        return {
            'action': action,
            'details': details,
            'risk_level': score.risk_level,
            'targets': {
                'entry': score.details.get('current_price', 0),
                'stop_loss': score.details.get('current_price', 0) * 0.95,
                'target_1': score.details.get('current_price', 0) * 1.10,
                'target_2': score.details.get('current_price', 0) * 1.20
            }
        }
    
    def scan_multiple(self, symbols: List[str], data_provider=None) -> pd.DataFrame:
        """
        مسح عدة أسهم
        
        Args:
            symbols: قائمة الرموز
            data_provider: مزود البيانات (اختياري)
        
        Returns:
            DataFrame بالنتائج
        """
        results = []
        
        for symbol in symbols:
            try:
                # جلب البيانات
                if data_provider:
                    df = data_provider(symbol).get_history(period="6mo")
                else:
                    # محاولة استخدام yfinance
                    import yfinance as yf
                    df = yf.Ticker(symbol).history(period="6mo")
                
                if df.empty:
                    continue
                
                # تحليل السهم
                analysis = self.analyze(df, symbol)
                
                if 'error' not in analysis:
                    results.append({
                        'symbol': symbol,
                        'score': analysis['score']['total_score'],
                        'rating': analysis['score']['rating'],
                        'signal': analysis['score']['signal'],
                        'risk': analysis['score']['risk_level'],
                        'confidence': analysis['score']['confidence'],
                        'squeeze': analysis['score']['squeeze_score'],
                        'breakout': analysis['score']['breakout_probability'],
                        'volume': analysis['score']['volume_score'],
                        'smart_money': analysis['score']['smart_money_score'],
                        'recommendation': analysis['recommendation']['action']
                    })
                    
            except Exception as e:
                print(f"⚠️ خطأ في تحليل {symbol}: {e}")
                continue
        
        if results:
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values('score', ascending=False)
            return df_results
        
        return pd.DataFrame()
