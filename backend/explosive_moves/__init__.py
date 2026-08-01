# backend/explosive_moves/__init__.py
"""
وحدة اكتشاف الحركات السعرية المتفجرة (Explosive Moves)
تم تحصين الملف لمنع انهيار الواجهة في حال عدم اكتمال باقي الملفات الفرعية.
"""

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


__all__ = [
    'detect_squeeze',
    'VolatilityAnalyzer',
    'CompressionAnalyzer',
    'BreakoutProbability',
    'VolumeExpansion',
    'SmartMoneyAnalyzer',
    'OptionsFlowAnalyzer',
    'AIPredictor',
    'ExplosiveScore'
]

__version__ = '1.0.0'
