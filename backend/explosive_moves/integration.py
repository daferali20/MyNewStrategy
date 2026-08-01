# backend/explosive_moves/integration.py
"""
وحدة التكامل الشاملة للحركات المتفجرة
تربط جميع موديولات التحليل (Squeeze, Volatility, Smart Money, etc.) 
لتوفير تقرير متكامل لكل سهم.
"""

import pandas as pd
from typing import Dict, Any

from .squeeze_detector import detect_squeeze
from .score import ExplosiveScore

def analyze_explosive_potential(df: pd.DataFrame) -> Dict[str, Any]:
    """
    تحليل كامل للسهم لإيجاد إمكانية الحركة المتفجرة
    """
    if df is None or df.empty or len(df) < 20:
        return {
            "symbol_status": "INSUFFICIENT_DATA",
            "explosive_score": 0,
            "is_squeeze": False,
            "breakout_prob": 0.0
        }
    
    # 1. تحليل الانضغاط
    squeeze_res = detect_squeeze(df)
    
    # 2. احتساب الدرجة الكلية (Explosive Score)
    # يتم حساب الدرجة سياقياً بناءً على نتائج الموديولات المفعلة
    score_calculator = ExplosiveScore() if 'ExplosiveScore' in globals() else None
    
    if score_calculator and hasattr(score_calculator, 'calculate'):
        final_score = score_calculator.calculate(df, squeeze_res)
    else:
        # حساب تقريبي احتياطي عند التجميع
        base_score = squeeze_res.get("squeeze_score", 0)
        final_score = min(100.0, base_score * 1.2)
        
    return {
        "is_squeeze": squeeze_res.get("is_squeezed", False),
        "squeeze_score": squeeze_res.get("squeeze_score", 0.0),
        "squeeze_duration": squeeze_res.get("squeeze_duration", 0),
        "momentum_dir": squeeze_res.get("momentum_dir", "NEUTRAL"),
        "explosive_score": round(final_score, 1),
        "breakout_prob": round(min(99.0, final_score * 0.9), 1)
    }
