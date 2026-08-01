# backend/scanner/intraday_scanner.py
"""
الماسح الضوئي للانفجار داخل اليوم - Intraday Breakout Scanner
يكتشف فرص الاختراق على فريمات زمنية قصيرة (5 دقائق، 15 دقيقة، ساعة)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# نماذج البيانات
# ============================================================================

@dataclass
class IntradaySignal:
    """إشارة انفجار داخل اليوم"""
    symbol: str
    timeframe: str  # '5min', '15min', '1h'
    breakout_price: float
    current_price: float
    volume_surge: float
    vwap_break: bool
    rsi: float
    macd_cross: bool
    resistance_level: float
    support_level: float
    stop_loss: float
    target_1: float
    target_2: float
    score: float
    timestamp: datetime = datetime.now()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = data['timestamp'].isoformat()
        return data


# ============================================================================
# الماسح الداخلي اليوم
# ============================================================================

class IntradayScanner:
    """
    ماسح الانفجار داخل اليوم
    يكتشف فرص الاختراق على فريمات زمنية قصيرة
    """
    
    def __init__(self,
                 volume_surge_threshold: float = 1.5,
                 rsi_min: float = 40,
                 rsi_max: float = 70,
                 lookback_bars: int = 20,
                 atr_multiplier: float = 1.0):
        """
        Args:
            volume_surge_threshold: عتبة زيادة الحجم
            rsi_min: الحد الأدنى لـ RSI
            rsi_max: الحد الأقصى لـ RSI
            lookback_bars: عدد الشموع للنظر للخلف
            atr_multiplier: مضاعف ATR
        """
        self.volume_surge_threshold = volume_surge_threshold
        self.rsi_min = rsi_min
        self.rsi_max = rsi_max
        self.lookback_bars = lookback_bars
        self.atr_multiplier = atr_multiplier
    
    def analyze(self, df: pd.DataFrame, symbol: str = "UNKNOWN",
                timeframe: str = "15min") -> Optional[IntradaySignal]:
        """
        تحليل الانفجار داخل اليوم
        
        Args:
            df: DataFrame مع بيانات OHLCV
            symbol: رمز السهم
            timeframe: الفريم الزمني
        
        Returns:
            IntradaySignal أو None
        """
        if not self._validate_data(df):
            return None
        
        try:
            # حساب المؤشرات
            indicators = self._calculate_indicators(df)
            if indicators is None:
                return None
            
            # تقييم الشروط
            is_signal = all([
                indicators['volume_surge'] >= self.volume_surge_threshold,
                self.rsi_min <= indicators['rsi'] <= self.rsi_max,
                indicators['vwap_break']
            ])
            
            if not is_signal:
                return None
            
            # حساب المستويات
            levels = self._calculate_levels(df)
            
            # حساب الدرجة
            score = self._calculate_score(indicators)
            
            return IntradaySignal(
                symbol=symbol,
                timeframe=timeframe,
                breakout_price=levels['resistance'],
                current_price=indicators['current_price'],
                volume_surge=round(indicators['volume_surge'], 2),
                vwap_break=indicators['vwap_break'],
                rsi=round(indicators['rsi'], 2),
                macd_cross=indicators['macd_cross'],
                resistance_level=round(levels['resistance'], 2),
                support_level=round(levels['support'], 2),
                stop_loss=round(levels['stop_loss'], 2),
                target_1=round(levels['target_1'], 2),
                target_2=round(levels['target_2'], 2),
                score=round(score, 2)
            )
            
        except Exception as e:
            print(f"⚠️ خطأ في التحليل الداخلي اليومي: {e}")
            return None
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """التحقق من صحة البيانات"""
        if df is None or len(df) < 30:
            return False
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        return all(col in df.columns for col in required_cols)
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Optional[Dict]:
        """حساب المؤشرات الفنية داخل اليوم"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # 1. حجم التداول
        avg_volume = volume.iloc[-self.lookback_bars-1:-1].mean()
        current_volume = volume.iloc[-1]
        volume_surge = current_volume / avg_volume if avg_volume > 0 else 0
        
        # 2. VWAP (متوسط السعر المرجح بالحجم)
        typical_price = (high + low + close) / 3
        cumulative_vwap = (typical_price * volume).cumsum() / volume.cumsum()
        current_vwap = cumulative_vwap.iloc[-1]
        current_price = close.iloc[-1]
        vwap_break = current_price > current_vwap
        
        # 3. RSI سريع (فترة 7)
        rsi = self._calculate_rsi(close, period=7)
        if rsi is None:
            return None
        
        # 4. MACD سريع
        macd_cross = self._calculate_macd_cross(close)
        
        return {
            'volume_surge': volume_surge,
            'current_price': current_price,
            'vwap_break': vwap_break,
            'rsi': rsi,
            'macd_cross': macd_cross
        }
    
    def _calculate_rsi(self, close: pd.Series, period: int = 7) -> Optional[float]:
        """حساب RSI سريع"""
        try:
            delta = close.diff()
            gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
            
            loss = loss.replace(0, np.nan)
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            last_rsi = rsi.iloc[-1]
            return float(last_rsi) if not pd.isna(last_rsi) else None
            
        except Exception:
            return None
    
    def _calculate_macd_cross(self, close: pd.Series) -> bool:
        """التحقق من تقاطع MACD"""
        try:
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            
            # التحقق من تقاطع إيجابي (المؤشر فوق خط الإشارة)
            return macd_line.iloc[-1] > signal_line.iloc[-1]
        except Exception:
            return False
    
    def _calculate_levels(self, df: pd.DataFrame) -> Dict:
        """حساب مستويات الدعم والمقاومة"""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        # المقاومة: أعلى سعر في آخر 10 شموع
        resistance = high.iloc[-10:].max()
        
        # الدعم: أدنى سعر في آخر 10 شموع
        support = low.iloc[-10:].min()
        
        # حساب ATR
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]
        
        current_price = close.iloc[-1]
        
        # وقف الخسارة
        stop_loss = min(support, current_price - (atr * self.atr_multiplier))
        
        # الأهداف
        risk = resistance - stop_loss
        target_1 = resistance + (risk * 1.0)
        target_2 = resistance + (risk * 2.0)
        
        return {
            'resistance': resistance,
            'support': support,
            'stop_loss': stop_loss,
            'target_1': target_1,
            'target_2': target_2
        }
    
    def _calculate_score(self, indicators: Dict) -> float:
        """حساب درجة الإشارة"""
        score = 0.0
        
        # 1. زيادة الحجم (30%)
        volume_score = min(100, indicators['volume_surge'] * 40)
        score += volume_score * 0.30
        
        # 2. اختراق VWAP (25%)
        score += 100 if indicators['vwap_break'] else 0
        score *= 0.25
        
        # 3. RSI (25%)
        if indicators['rsi'] is not None:
            if 50 <= indicators['rsi'] <= 60:
                rsi_score = 100
            else:
                rsi_score = max(0, 100 - abs(
