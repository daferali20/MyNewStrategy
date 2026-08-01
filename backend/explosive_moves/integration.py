# backend/explosive_moves/integration.py
"""
وحدة التكامل الشاملة للحركات المتفجرة (Explosive Moves Integration Module)
تربط جميع موديولات التحليل (Squeeze, Volatility, Options Flow, Smart Money, etc.) 
لتوفير تقرير متكامل وشامل لكل سهم.
"""

from typing import Dict, Any, Optional
import pandas as pd

from .squeeze_detector import detect_squeeze
from .options_flow import OptionsFlowAnalyzer

# محاولة استيراد حساب الدرجة التفصيلية مع وجود البديل
try:
    from .score import ExplosiveScore
except ImportError:
    ExplosiveScore = None


def analyze_explosive_potential(df: pd.DataFrame, symbol: str = "ASSET") -> Dict[str, Any]:
    """
    تحليل كامل للسهم لإيجاد إمكانية وتوقع الحركة المتفجرة (Explosive Move)

    Args:
        df: DataFrame يحتوي على بيانات الأسعار التاريخية (OHLCV)
        symbol: رمز السهم/الأصل المالي المراد تحليله

    Returns:
        Dict يضم جميع المؤشرات المجمعة والدرجة النهائية واحتمالية الاختراق
    """
    # التحقق من كفاية وصحة البيانات
    if df is None or df.empty or len(df) < 20:
        return {
            "symbol": symbol,
            "symbol_status": "INSUFFICIENT_DATA",
            "explosive_score": 0.0,
            "is_squeeze": False,
            "breakout_prob": 0.0,
            "sentiment": "NEUTRAL",
            "options_summary": {}
        }

    # 1. تحليل انضغاط الذبذبة (Squeeze Detection)
    squeeze_res = detect_squeeze(df)

    # 2. تحليل تدفق الخيارات والسيولة الذكية (Options Flow Analysis)
    options_analyzer = OptionsFlowAnalyzer()
    options_res = options_analyzer.analyze(symbol)

    # 3. احتساب الدرجة الكلية (Explosive Score)
    if ExplosiveScore is not None:
        try:
            score_calculator = ExplosiveScore()
            # إمكانية تمرير نتائج الخيارات أيضاً إن دعمها حساب الدرجة
            if hasattr(score_calculator, 'calculate'):
                final_score = score_calculator.calculate(df, squeeze_res)
            else:
                final_score = _fallback_score(squeeze_res, options_res)
        except Exception:
            final_score = _fallback_score(squeeze_res, options_res)
    else:
        final_score = _fallback_score(squeeze_res, options_res)

    # حساب احتمالية الاختراق وتحديد الاتجاه المرجح
    breakout_probability = min(99.0, max(5.0, final_score * 0.95))
    momentum_direction = squeeze_res.get("momentum_dir", "NEUTRAL")

    return {
        "symbol": symbol,
        "symbol_status": "READY",
        "is_squeeze": bool(squeeze_res.get("is_squeezed", False)),
        "squeeze_score": round(float(squeeze_res.get("squeeze_score", 0.0)), 1),
        "squeeze_duration": int(squeeze_res.get("squeeze_duration", 0)),
        "momentum_dir": momentum_direction,
        "options_sentiment": options_res.get("sentiment", "محايد 📊"),
        "options_score": round(float(options_res.get("smart_money_score", 50.0)), 1),
        "call_put_ratio": options_res.get("call_put_ratio", 1.0),
        "unusual_options_activity": options_res.get("unusual_activity", False),
        "explosive_score": round(float(final_score), 1),
        "breakout_prob": round(float(breakout_probability), 1)
    }


def _fallback_score(squeeze_res: Dict, options_res: Dict) -> float:
    """حساب تقريبي احتياطي للدرجة الكلية عند تعذر استخدام ExplosiveScore"""
    squeeze_val = squeeze_res.get("squeeze_score", 0.0)
    options_val = options_res.get("smart_money_score", 50.0)

    # وزني: 60% للانضغاط و 40% لتدفق الخيارات
    combined = (squeeze_val * 0.6) + (options_val * 0.4)
    return float(min(100.0, max(0.0, combined)))
