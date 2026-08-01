# backend/scanner/screener.py
"""
الماسح الذكي للأسهم - فلترة وتحليل متقدم
"""

import sys
import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إضافة المجلد الرئيسي للمشروع
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# استيراد الموديولات الداخلية
try:
    from backend.data_providers.market_data import USMarketDataProvider
    from backend.analysis.technical import TechnicalAnalyzer
    from backend.scanner.breakout_scanner import BreakoutScanner, BreakoutIndicators
except ImportError as e:
    logger.error(f"⚠️ فشل في استيراد الوحدات الداخلية: {e}")
    raise


# ============================================================================
# نماذج البيانات
# ============================================================================

@dataclass
class ScanResult:
    """نتيجة المسح لسهم واحد"""
    symbol: str
    close: float
    rsi: float
    trend: str
    macd_signal: str
    volume_ratio: float
    breakout_score: float
    scan_time: datetime = datetime.now()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['scan_time'] = data['scan_time'].isoformat()
        return data


# ============================================================================
# الماسح الذكي
# ============================================================================

class SmartScanner:
    """
    الماسح الذكي للأسهم
    يقوم بتحليل الأسهم وتصفيتها وفق معايير متعددة
    """
    
    def __init__(self, symbols: List[str], cache_duration: int = 300):
        """
        Args:
            symbols: قائمة رموز الأسهم
            cache_duration: مدة صلاحية الكاش بالثواني
        """
        self.symbols = symbols
        self.cache_duration = cache_duration
        self._cache = {}
        self._last_scan = None
        self.breakout_scanner = BreakoutScanner()
    
    def _is_cache_valid(self) -> bool:
        """التحقق من صلاحية الكاش"""
        if self._last_scan is None:
            return False
        elapsed = (datetime.now() - self._last_scan).total_seconds()
        return elapsed < self.cache_duration
    
    def _analyze_symbol(self, symbol: str) -> Optional[ScanResult]:
        """تحليل سهم فردي"""
        try:
            # 1. جلب البيانات
            provider = USMarketDataProvider(symbol)
            df = provider.get_history(period="6mo")
            
            if df is None or df.empty or len(df) < 50:
                logger.warning(f"⚠️ بيانات غير كافية للسهم {symbol}")
                return None
            
            # 2. التحليل الفني الأساسي
            from backend.analysis.technical import TechnicalAnalyzer
            analyzer = TechnicalAnalyzer(df)
            analysis = analyzer.analyze_trend()
            
            if not analysis or not isinstance(analysis, dict):
                return None
            
            # 3. تحليل الانفجار
            is_breakout, indicators = self.breakout_scanner.analyze(df)
            
            # 4. استخراج النتائج
            rsi = float(analysis.get("rsi_value", 50.0))
            trend = str(analysis.get("trend", "غير معروف"))
            macd_signal = str(analysis.get("macd_signal", "محايد"))
            last_close = df['Close'].iloc[-1]
            
            volume_ratio = indicators.volume_ratio if indicators else 1.0
            breakout_score = indicators.score if indicators and is_breakout else 0.0
            
            return ScanResult(
                symbol=symbol,
                close=round(float(last_close), 2),
                rsi=round(rsi, 2),
                trend=trend,
                macd_signal=macd_signal,
                volume_ratio=volume_ratio,
                breakout_score=breakout_score
            )
            
        except Exception as e:
            logger.error(f"⚠️ تعذر تحليل السهم {symbol}: {e}")
            return None
    
    def scan_market(self,
                   min_rsi: float = 0,
                   max_rsi: float = 100,
                   trend_filter: str = "الكل",
                   min_breakout_score: float = 60,
                   use_cache: bool = True) -> List[Dict]:
        """
        مسح السوق وتصفية الأسهم حسب المعايير
        
        Args:
            min_rsi: الحد الأدنى لـ RSI
            max_rsi: الحد الأقصى لـ RSI
            trend_filter: "الكل" أو "صاعد" أو "هابط" أو "جانبي"
            min_breakout_score: الحد الأدنى لدرجة الانفجار
            use_cache: استخدام النتائج المخزنة مؤقتاً
        
        Returns:
            قائمة بالنتائج كقاموس
        """
        if use_cache and self._is_cache_valid():
            logger.info("📦 استخدام النتائج المخزنة مؤقتاً")
            return self._cache
        
        logger.info(f"🔍 بدء مسح {len(self.symbols)} سهماً...")
        results = []
        
        for sym in self.symbols:
            result = self._analyze_symbol(sym)
            if result is None:
                continue
            
            # تطبيق شروط الفلترة
            if min_rsi <= result.rsi <= max_rsi:
                if trend_filter == "الكل" or (trend_filter in result.trend):
                    if result.breakout_score >= min_breakout_score:
                        results.append(result.to_dict())
        
        logger.info(f"✅ اكتمل المسح: تم العثور على {len(results)} سهماً مطابقة")
        
        # تحديث الكاش
        self._cache = results
        self._last_scan = datetime.now()
        
        return results
    
    def get_summary(self, results: List[Dict]) -> Dict:
        """الحصول على ملخص للنتائج"""
        if not results:
            return {"count": 0, "avg_rsi": 0, "avg_breakout_score": 0, "trends": {}}
        
        rsi_values = [r.get("rsi", 0) for r in results]
        breakout_scores = [r.get("breakout_score", 0) for r in results]
        
        trends = {}
        for r in results:
            trend = r.get("trend", "غير معروف")
            trends[trend] = trends.get(trend, 0) + 1
        
        return {
            "count": len(results),
            "avg_rsi": round(sum(rsi_values) / len(rsi_values), 2),
            "avg_breakout_score": round(sum(breakout_scores) / len(breakout_scores), 2),
            "min_rsi": min(rsi_values),
            "max_rsi": max(rsi_values),
            "trends": trends,
            "scan_time": datetime.now().isoformat()
        }


# ============================================================================
# دوال مساعدة
# ============================================================================

def quick_scan(symbols: List[str],
              min_rsi: int = 50,
              max_rsi: int = 70,
              min_score: float = 65) -> List[Dict]:
    """دالة سريعة للمسح بمعايير افتراضية"""
    scanner = SmartScanner(symbols)
    return scanner.scan_market(
        min_rsi=min_rsi,
        max_rsi=max_rsi,
        trend_filter="صاعد",
        min_breakout_score=min_score
    )


def scan_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """مسح من DataFrame مباشرة"""
    scanner = BreakoutScanner()
    results = []
    
    # محاكاة تحليل كل سهم (في الواقع df يحتوي على بيانات سهم واحد)
    is_breakout, indicators = scanner.analyze(df)
    
    if is_breakout and indicators:
        results.append({
            'is_breakout': True,
            'score': indicators.score,
            'squeeze': indicators.is_squeeze,
            'volume_ratio': indicators.volume_ratio,
            'rsi': indicators.rsi,
            'entry': indicators.entry_point,
            'stop_loss': indicators.stop_loss,
            'target_1': indicators.target_1,
            'target_2': indicators.target_2
        })
    
    return pd.DataFrame(results)
