# backend/explosive_moves/__init__.py
"""
وحدة اكتشاف الحركات السعرية المتفجرة (Explosive Moves)
تحليل شامل للضغط، التقلبات، والانفجارات السعرية
"""

from .squeeze_detector import SqueezeDetector
from .volatility import VolatilityAnalyzer
from .compression import CompressionAnalyzer
from .breakout_probability import BreakoutProbability
from .volume_expansion import VolumeExpansion
from .smart_money import SmartMoneyAnalyzer
from .options_flow import OptionsFlowAnalyzer
from .ai_predictor import AIPredictor
from .score import ExplosiveScore

__all__ = [
    'SqueezeDetector',
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
