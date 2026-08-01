# backend/explosive_moves/__init__.py
"""
وحدة اكتشاف الحركات السعرية المتفجرة (Explosive Moves Engine)
تم تحصين الملف باستيراد آمن لتفادي انهيار الواجهة، مع توفير نقطة دخول موحدة للتحليل.
"""

from typing import Dict, Any, Optional
import pandas as pd

# استيراد آمن لـ Squeeze Detector
try:
    from .squeeze_detector import detect_squeeze
except ImportError:
    detect_squeeze = None

# استيراد آمن لـ Volatility
try:
    from .volatility import VolatilityAnalyzer
except ImportError:
    VolatilityAnalyzer = None

# استيراد آمن لـ Compression
try:
    from .compression import CompressionAnalyzer
except ImportError:
    CompressionAnalyzer = None

# استيراد آمن لـ Breakout Probability
try:
    from .breakout_probability import BreakoutProbability
except ImportError:
    BreakoutProbability = None

# استيراد آمن لـ Volume Expansion
try:
    from .volume_expansion import VolumeExpansion
except ImportError:
    VolumeExpansion = None

# استيراد آمن لـ Smart Money
try:
    from .smart_money import SmartMoneyAnalyzer
except ImportError:
    SmartMoneyAnalyzer = None

# استيراد آمن لـ Options Flow
try:
    from .options_flow import OptionsFlowAnalyzer
except ImportError:
    OptionsFlowAnalyzer = None

# استيراد آمن لـ AI Predictor
try:
    from .ai_predictor import AIPredictor
except ImportError:
    AIPredictor = None

# استيراد آمن لـ Explosive Score
try:
    from .score import ExplosiveScore
except ImportError:
    ExplosiveScore = None


def analyze_explosive_setup(df: pd.DataFrame, symbol: str = "TICKER") -> Dict[str, Any]:
    """
    واجهة برمجية موحدة (Unified Facade) لجمع كافة تحليلات الانفجار السعري لرمز محدد.
    
    Args:
        df: DataFrame بالأسعار (OHLCV)
        symbol: رمز السهم/الرمز السعري
        
    Returns:
        Dict يحتوي على كافة النتائج والتنبؤات المجمعة
    """
    results: Dict[str, Any] = {
        'symbol': symbol,
        'has_data': not (df is None or df.empty),
        'squeeze': None,
        'compression': None,
        'probability': None,
        'ai_prediction': None,
        'explosive_score': 0.0
    }

    if df is None or df.empty or len(df) < 20:
        results['error'] = 'بيانات غير كافية لإجراء التحليل المتفجر'
        return results

    # 1. تحليل Squeeze
    if detect_squeeze is not None:
        try:
            results['squeeze'] = detect_squeeze(df)
        except Exception as e:
            results['squeeze'] = {'error': str(e)}

    # 2. تحليل Compression
    if CompressionAnalyzer is not None:
        try:
            analyzer = CompressionAnalyzer()
            results['compression'] = analyzer.analyze(df)
        except Exception as e:
            results['compression'] = {'error': str(e)}

    # 3. حساب الاحتمالية AI & Breakout
    indicators = {}
    if isinstance(results.get('compression'), dict) and 'compression_score' in results['compression']:
        indicators['compression_score'] = results['compression']['compression_score']
    if isinstance(results.get('squeeze'), dict) and 'squeeze_score' in results['squeeze']:
        indicators['squeeze_score'] = results['squeeze']['squeeze_score']

    if BreakoutProbability is not None:
        try:
            calc = BreakoutProbability()
            results['probability'] = calc.calculate(df, indicators=indicators)
        except Exception as e:
            results['probability'] = {'error': str(e)}

    if AIPredictor is not None:
        try:
            predictor = AIPredictor()
            results['ai_prediction'] = predictor.predict(indicators)
        except Exception as e:
            results['ai_prediction'] = {'error': str(e)}

    # 4. التقييم النهائي (Explosive Score)
    if ExplosiveScore is not None:
        try:
            score_engine = ExplosiveScore()
            results['explosive_score'] = score_engine.calculate(df, indicators=results)
        except Exception:
            prob = results.get('probability', {}).get('probability', 50.0) if isinstance(results.get('probability'), dict) else 50.0
            results['explosive_score'] = prob

    return results


__all__ = [
    'detect_squeeze',
    'VolatilityAnalyzer',
    'CompressionAnalyzer',
    'BreakoutProbability',
    'VolumeExpansion',
    'SmartMoneyAnalyzer',
    'OptionsFlowAnalyzer',
    'AIPredictor',
    'ExplosiveScore',
    'analyze_explosive_setup'
]

__version__ = '1.1.0'
