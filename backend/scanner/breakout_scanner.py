# backend/scanner/breakout_scanner.py
"""
الماسح الضوئي للانفجار السعري - اكتشاف الأسهم الجاهزة للاختراق
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# البيانات الأساسية
# ============================================================================

@dataclass
class BreakoutIndicators:
    """مؤشرات الانفجار السعري"""
    is_squeeze: bool
    bandwidth: float
    bandwidth_change: float
    unusual_volume: bool
    volume_ratio: float
    rsi: float
    near_high: bool
    price_position: float
    score: float
    entry_point: float
    stop_loss: float
    target_1: float
    target_2: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# الماسح الرئيسي
# ============================================================================

class BreakoutScanner:
    """
    ماسح الانفجار السعري المتقدم
    يكتشف الأسهم الجاهزة للاختراق بناءً على معايير متعددة
    """
    
    def __init__(self,
                 squeeze_threshold: float = 1.20,
                 volume_threshold: float = 2.0,
                 rsi_min: float = 45,
                 rsi_max: float = 75,
                 near_high_threshold: float = 0.88,
                 lookback_days: int = 252,
                 atr_multiplier_sl: float = 1.5,
                 target_multiplier: float = 2.0):
        """
        Args:
            squeeze_threshold: عتبة الانضغاط (كلما قلت كانت أدق)
            volume_threshold: مضاعف الحجم غير الطبيعي
            rsi_min: الحد الأدنى لـ RSI
            rsi_max: الحد الأقصى لـ RSI
            near_high_threshold: نسبة القرب من أعلى سعر
            lookback_days: فترة النظر للخلف
            atr_multiplier_sl: مضاعف ATR لوقف الخسارة
            target_multiplier: مضاعف الهدف بالنسبة لوقف الخسارة
        """
        self.squeeze_threshold = squeeze_threshold
        self.volume_threshold = volume_threshold
        self.rsi_min = rsi_min
        self.rsi_max = rsi_max
        self.near_high_threshold = near_high_threshold
        self.lookback_days = lookback_days
        self.atr_multiplier_sl = atr_multiplier_sl
        self.target_multiplier = target_multiplier
    
    def analyze(self, df: pd.DataFrame) -> Tuple[bool, Optional[BreakoutIndicators]]:
        """
        تحليل شامل للانفجار السعري
        
        Returns:
            (is_breakout, indicators)
        """
        if not self._validate_data(df):
            return False, None
        
        try:
            indicators = self._calculate_indicators(df)
            if indicators is None:
                return False, None
            
            # تقييم الشروط الأساسية
            is_breakout = all([
                indicators.is_squeeze,
                indicators.unusual_volume,
                self.rsi_min <= indicators.rsi <= self.rsi_max,
                indicators.near_high
            ])
            
            # حساب درجة الجاهزية
            indicators.score = self._calculate_score(indicators)
            
            # حساب مستويات الدخول
            self._calculate_levels(df, indicators)
            
            return is_breakout, indicators
            
        except Exception as e:
            print(f"⚠️ خطأ في تحليل الانفجار: {e}")
            return False, None
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """التحقق من صحة البيانات"""
        if df is None or len(df) < 50:
            return False
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        return all(col in df.columns for col in required_cols)
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Optional[BreakoutIndicators]:
        """حساب جميع المؤشرات الفنية"""
        close = df['Close']
        high = df['High']
        volume = df['Volume']
        
        # 1. Bollinger Bands
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        band_width = (bb_upper - bb_lower) / sma_20
        
        if band_width.iloc[-1] is None or band_width.iloc[-51:-1].min() is None:
            return None
        
        current_bandwidth = band_width.iloc[-1]
        min_bandwidth_prev = band_width.iloc[-51:-1].min()
        
        is_squeeze = current_bandwidth <= (min_bandwidth_prev * self.squeeze_threshold)
        bandwidth_change = ((current_bandwidth - min_bandwidth_prev) / min_bandwidth_prev * 100) if min_bandwidth_prev > 0 else 0
        
        # 2. حجم التداول
        avg_volume_20 = volume.iloc[-21:-1].mean()
        current_volume = volume.iloc[-1]
        
        if avg_volume_20 > 0:
            volume_ratio = current_volume / avg_volume_20
            unusual_volume = volume_ratio >= self.volume_threshold
        else:
            volume_ratio = 0
            unusual_volume = False
        
        # 3. RSI
        rsi = self._calculate_rsi(close)
        if rsi is None:
            return None
        
        # 4. القرب من أعلى سعر
        high_period = high.iloc[-self.lookback_days:].max()
        current_price = close.iloc[-1]
        
        if high_period > 0:
            price_position = current_price / high_period
            near_high = price_position >= self.near_high_threshold
        else:
            price_position = 0
            near_high = False
        
        return BreakoutIndicators(
            is_squeeze=is_squeeze,
            bandwidth=round(current_bandwidth, 4),
            bandwidth_change=round(bandwidth_change, 2),
            unusual_volume=unusual_volume,
            volume_ratio=round(volume_ratio, 2),
            rsi=round(rsi, 2),
            near_high=near_high,
            price_position=round(price_position * 100, 2),
            score=0.0,
            entry_point=0.0,
            stop_loss=0.0,
            target_1=0.0,
            target_2=0.0
        )
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> Optional[float]:
        """حساب RSI يدوياً"""
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
    
    def _calculate_score(self, indicators: BreakoutIndicators) -> float:
        """حساب درجة الجاهزية (0-100)"""
        score = 0.0
        
        # 1. درجة الانضغاط (30%)
        if indicators.is_squeeze:
            squeeze_strength = min(100, (1 / indicators.bandwidth) * 10) if indicators.bandwidth > 0 else 0
            score += squeeze_strength * 0.30
        
        # 2. درجة حجم التداول (25%)
        volume_score = min(100, indicators.volume_ratio * 30) if indicators.volume_ratio > 0 else 0
        score += volume_score * 0.25
        
        # 3. درجة RSI (20%)
        if indicators.rsi is not None:
            if 50 <= indicators.rsi <= 60:
                rsi_score = 100
            elif 45 <= indicators.rsi < 50:
                rsi_score = 70
            elif 60 < indicators.rsi <= 70:
                rsi_score = 80
            elif 70 < indicators.rsi <= 75:
                rsi_score = 60
            else:
                rsi_score = max(0, 100 - abs(indicators.rsi - 55) * 2)
            score += rsi_score * 0.20
        
        # 4. درجة القرب من القمة (15%)
        price_score = indicators.price_position * 100 if indicators.price_position > 0 else 0
        score += price_score * 0.15
        
        # 5. درجة اتجاه الانضغاط (10%)
        if indicators.bandwidth_change < 0:
            trend_score = min(100, abs(indicators.bandwidth_change) * 2)
        else:
            trend_score = max(0, 100 - indicators.bandwidth_change * 2)
        score += trend_score * 0.10
        
        return round(min(100, score), 2)
    
    def _calculate_levels(self, df: pd.DataFrame, indicators: BreakoutIndicators):
        """حساب مستويات الدخول والخروج"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # حساب ATR
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]
        
        current_price = close.iloc[-1]
        
        # نقطة الدخول: أعلى سعر في آخر 20 يوم + (ATR * 0.5)
        resistance = high.iloc[-20:].max()
        indicators.entry_point = round(resistance + (atr * 0.5), 2)
        
        # وقف الخسارة: أدنى سعر في آخر 10 أيام
        support = low.iloc[-10:].min()
        indicators.stop_loss = round(min(support, current_price - (atr * self.atr_multiplier_sl)), 2)
        
        # الأهداف
        risk = indicators.entry_point - indicators.stop_loss
        indicators.target_1 = round(indicators.entry_point + (risk * self.target_multiplier), 2)
        indicators.target_2 = round(indicators.entry_point + (risk * self.target_multiplier * 1.5), 2)


# ============================================================================
# دوال مساعدة للتكامل مع Streamlit
# ============================================================================

def scan_for_potential_breakouts(df: pd.DataFrame) -> bool:
    """دالة متوافقة مع الكود السابق"""
    scanner = BreakoutScanner()
    is_breakout, _ = scanner.analyze(df)
    return is_breakout


def get_breakout_candidates(symbols: List[str] = None, 
                           data_provider=None,
                           min_score: float = 60) -> pd.DataFrame:
    """
    جلب مرشحي الانفجار من السوق
    
    Args:
        symbols: قائمة الرموز (إذا كان None، يستخدم قائمة افتراضية)
        data_provider: مزود البيانات (إذا كان None، يستخدم yfinance)
        min_score: الحد الأدنى للدرجة
    
    Returns:
        DataFrame بالمرشحين
    """
    # قائمة افتراضية للأسهم الأمريكية
    default_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD',
        'INTC', 'NFLX', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'CSCO',
        'QCOM', 'TXN', 'AVGO', 'INTU', 'AMAT', 'LRCX', 'MU', 'NOW',
        'PANW', 'SNPS', 'CDNS', 'MCHP', 'ADI', 'NXPI'
    ]
    
    symbols = symbols or default_symbols
    
    # استيراد مزود البيانات
    if data_provider is None:
        try:
            from backend.data_providers.market_data import USMarketDataProvider
            data_provider = USMarketDataProvider
        except ImportError:
            # محاولة استخدام yfinance مباشرة
            import yfinance as yf
            data_provider = yf.Ticker
    
    scanner = BreakoutScanner()
    candidates = []
    
    for symbol in symbols[:20]:  # حد للسرعة
        try:
            # جلب البيانات
            if hasattr(data_provider, 'get_history'):
                df = data_provider(symbol).get_history(period="6mo")
            else:
                df = data_provider(symbol).history(period="6mo")
            
            if df is None or df.empty:
                continue
            
            is_breakout, indicators = scanner.analyze(df)
            
            if is_breakout and indicators and indicators.score >= min_score:
                candidates.append({
                    'Symbol': symbol,
                    'Current Price': df['Close'].iloc[-1],
                    'Breakout Score': indicators.score,
                    'Squeeze Status': '🔥 انضغاط حاد' if indicators.is_squeeze else '⚠️ انضغاط ضعيف',
                    'Volume Ratio': f"{indicators.volume_ratio:.1f}x",
                    'RSI': indicators.rsi,
                    'Entry Point': indicators.entry_point,
                    'Stop Loss': indicators.stop_loss,
                    'Target 1': indicators.target_1,
                    'Target 2': indicators.target_2
                })
                
        except Exception as e:
            print(f"⚠️ خطأ في تحليل {symbol}: {e}")
            continue
    
    if candidates:
        df_result = pd.DataFrame(candidates)
        df_result = df_result.sort_values('Breakout Score', ascending=False)
        return df_result
    
    return pd.DataFrame()


# ============================================================================
# مثال للاستخدام
# ============================================================================

if __name__ == "__main__":
    # اختبار الماسح
    import yfinance as yf
    
    print("🔍 اختبار الماسح الضوئي للانفجار...")
    
    # تحليل سهم واحد
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="6mo")
    
    scanner = BreakoutScanner()
    is_breakout, indicators = scanner.analyze(df)
    
    print(f"\n📊 تحليل AAPL:")
    print(f"هل هو انفجار؟ {is_breakout}")
    if indicators:
        print(f"الدرجة: {indicators.score}/100")
        print(f"حالة الانضغاط: {indicators.is_squeeze}")
        print(f"مضاعف الحجم: {indicators.volume_ratio}x")
        print(f"RSI: {indicators.rsi}")
        print(f"نقطة الدخول: ${indicators.entry_point:.2f}")
        print(f"وقف الخسارة: ${indicators.stop_loss:.2f}")
        print(f"الهدف 1: ${indicators.target_1:.2f}")
        print(f"الهدف 2: ${indicators.target_2:.2f}")
