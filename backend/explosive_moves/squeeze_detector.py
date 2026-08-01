# backend/explosive_moves/squeeze_detector.py
"""
مكتشف انضغاط السعر (Squeeze Detector)
يقوم بحساب انضغاط Bollinger Bands داخل Keltner Channels 
لاكتشاف فترات التجميع وتحديد جاهزية الانفجار السعري.
"""

import numpy as np
import pandas as pd
from typing import Dict, Union, Tuple


def calculate_bollinger_bands(
    df: pd.DataFrame, 
    period: int = 20, 
    std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series]:
    """حساب النطاق العلوي والسفلي لـ Bollinger Bands"""
    sma = df['close'].rolling(window=period).mean()
    rolling_std = df['close'].rolling(window=period).std()
    
    upper_bb = sma + (rolling_std * std_dev)
    lower_bb = sma - (rolling_std * std_dev)
    return upper_bb, lower_bb


def calculate_keltner_channels(
    df: pd.DataFrame, 
    period: int = 20, 
    atr_multiplier: float = 1.5
) -> Tuple[pd.Series, pd.Series]:
    """حساب قنوات Keltner Channels باستخدام متوسط النطاق الحقيقي (ATR)"""
    sma = df['close'].rolling(window=period).mean()
    
    # حساب True Range (TR)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    atr = tr.rolling(window=period).mean()
    
    upper_kc = sma + (atr * atr_multiplier)
    lower_kc = sma - (atr * atr_multiplier)
    return upper_kc, lower_kc


def detect_squeeze(
    df: pd.DataFrame, 
    bb_period: int = 20, 
    bb_std: float = 2.0, 
    kc_multiplier: float = 1.5
) -> Dict[str, Union[bool, float, int]]:
    """
    الدالة الرئيسية لاكتشاف انضغاط السعر.
    
    المُدخلات:
        df: DataFrame يحتوي على الأعمدة ['open', 'high', 'low', 'close', 'volume']
    
    المُخرجات:
        Dict يشتمل على:
        - is_squeezed: True إذا كان هناك انضغاط حالياً.
        - squeeze_score: درجة الانضغاط (0 إلى 100).
        - squeeze_duration: عدد الشمعات المتتالية في حالة انضغاط.
        - momentum_dir: اتجاه الزخم الحركي ("UP" أو "DOWN").
    """
    if df is None or df.empty or len(df) < bb_period:
        return {
            "is_squeezed": False,
            "squeeze_score": 0.0,
            "squeeze_duration": 0,
            "momentum_dir": "NEUTRAL"
        }
    
    df = df.copy()
    
    # 1. حساب المؤشرات
    upper_bb, lower_bb = calculate_bollinger_bands(df, period=bb_period, std_dev=bb_std)
    upper_kc, lower_kc = calculate_keltner_channels(df, period=bb_period, atr_multiplier=kc_multiplier)
    
    # 2. شرط الانضغاط: تكون Bollinger Bands بداخل Keltner Channels
    squeeze_on = (upper_bb < upper_kc) & (lower_bb > lower_kc)
    
    # 3. حساب قوة الانضغاط (كلما كانت BB أضيق بالنسبة لـ KC كان الانضغاط أقوى)
    bb_width = upper_bb - lower_bb
    kc_width = upper_kc - lower_kc
    
    # منع القسمة على صفر
    kc_width_safe = np.where(kc_width == 0, 1e-6, kc_width)
    squeeze_ratio = np.clip(1.0 - (bb_width / kc_width_safe), 0, 1)
    
    # 4. حساب مدة الانضغاط المتواصلة (Streak Duration)
    duration = 0
    for is_on in reversed(squeeze_on.values):
        if is_on:
            duration += 1
        else:
            break
            
    # 5. حساب مؤشر الزخم (Momentum Histogram)
    sma_period = df['close'].rolling(window=bb_period).mean()
    highest_high = df['high'].rolling(window=bb_period).max()
    lowest_low = df['low'].rolling(window=bb_period).min()
    val = df['close'] - ((highest_high + lowest_low) / 2 + sma_period) / 2
    
    latest_val = val.iloc[-1] if not val.empty else 0
    momentum_dir = "UP" if latest_val > 0 else "DOWN"
    
    # 6. حساب النتيجة النهائية من 0 إلى 100
    latest_is_squeezed = bool(squeeze_on.iloc[-1])
    score = float(squeeze_ratio.iloc[-1] * 100) if latest_is_squeezed else 0.0

    return {
        "is_squeezed": latest_is_squeezed,
        "squeeze_score": round(score, 2),
        "squeeze_duration": duration,
        "momentum_dir": momentum_dir
    }


# ============================================================================
# اختبار سريع للموديول عند التشغيل المستقل
# ============================================================================
if __name__ == "__main__":
    # إنشاء بيانات وهمية للاختبار
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
    sample_df = pd.DataFrame({
        'open': prices,
        'high': prices + 0.5,
        'low': prices - 0.5,
        'close': prices,
        'volume': 1000
    })
    
    result = detect_squeeze(sample_df)
    print("📋 نتيجة اختبار مكتشف الانضغاط:")
    print(result)
