# backend/scanner/screener.py
"""
الماسح الذكي للأسهم - فلترة وتحليل متقدم (نسخة آمنة ضد أخطاء None)
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
    from backend.scanner.breakout_scanner import BreakoutScanner
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
        if isinstance(data.get('scan_time'), datetime):
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
    
    def __init__(self, symbols: Optional[List[str]] = None, cache_duration: int = 300):
        """
        Args:
            symbols: قائمة رموز الأسهم
            cache_duration: مدة صلاحية الكاش بالثواني
        """
        self.symbols = symbols if symbols is not None else []
        self.cache_duration = cache_duration
        self._cache: List[Dict] = []
        self._last_scan: Optional[datetime] = None
        
        try:
            self.breakout_scanner = BreakoutScanner()
        except Exception as e:
            logger.error(f"⚠️ تعذر تهيئة BreakoutScanner: {e}")
            self.breakout_scanner = None
    
    def _is_cache_valid(self) -> bool:
        """التحقق من صلاحية الكاش"""
        if self._last_scan is None or self._cache is None:
            return False
        elapsed = (datetime.now() - self._last_scan).total_seconds()
        return elapsed < self.cache_duration
    
    def _analyze_symbol(self, symbol: str) -> Optional[ScanResult]:
        """تحليل سهم فردي بحماية متكاملة"""
        try:
            # 1. جلب البيانات
            provider = USMarketDataProvider(symbol)
            df = provider.get_history(period="6mo")
            
            if df is None or df.empty or len(df) < 50:
                logger.warning(f"⚠️ بيانات غير كافية للسهم {symbol}")
                return None
            
            # 2. التحليل الفني الأساسي
            analyzer = TechnicalAnalyzer(df)
            analysis = analyzer.analyze_trend()
            
            # حماية مشددة ضد القيمة الخالية None
            if analysis is None or not isinstance(analysis, dict):
                logger.warning(f"⚠️ فشل تحليل الاتجاه للسهم {symbol}")
                return None
            
            # 3. تحليل الانفجار
            is_breakout = False
            indicators = None
            if self.breakout_scanner:
                try:
                    res = self.breakout_scanner.analyze(df)
                    if res and isinstance(res, tuple) and len(res) == 2:
                        is_breakout, indicators = res
                except Exception as ex:
                    logger.warning(f"⚠️ خطأ أثناء تحليل الانفجار لـ {symbol}: {ex}")
            
            # 4. استخراج النتائج بأمان واستخدام قيم افتراضية
            rsi = float(analysis.get("rsi_value", 50.0) or 50.0)
            trend = str(analysis.get("trend", "غير معروف") or "غير معروف")
            macd_signal = str(analysis.get("macd_signal", "محايد") or "محايد")
            
            # التأكد من وجود عمود Close وقراءته بأمان
            if 'Close' in df.columns and not df['Close'].empty:
                last_close = float(df['Close'].iloc[-1])
            else:
                last_close = float(analysis.get("last_close", 0.0) or 0.0)
            
            volume_ratio = float(getattr(indicators, 'volume_ratio', 1.0) or 1.0)
            
            score_val = getattr(indicators, 'score', 0.0)
            breakout_score = float(score_val if (indicators and is_breakout and score_val is not None) else 0.0)
            
            return ScanResult(
                symbol=str(symbol),
                close=round(last_close, 2),
                rsi=round(rsi, 2),
                trend=trend,
                macd_signal=macd_signal,
                volume_ratio=round(volume_ratio, 2),
                breakout_score=round(breakout_score, 2)
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
        """
        if use_cache and self._is_cache_valid():
            logger.info("📦 استخدام النتائج المخزنة مؤقتاً")
            return self._cache if isinstance(self._cache, list) else []
        
        if not self.symbols:
            logger.warning("⚠️ لا توجد رموز أسهم في الماسح.")
            return []
            
        logger.info(f"🔍 بدء مسح {len(self.symbols)} سهماً...")
        results: List[Dict] = []
        
        for sym in self.symbols:
            result = self._analyze_symbol(sym)
            if result is None:
                continue
            
            # تطبيق شروط الفلترة بأسلوب آمن
            if min_rsi <= result.rsi <= max_rsi:
                if trend_filter == "الكل" or (trend_filter in result.trend):
                    if result.breakout_score >= min_breakout_score:
                        results.append(result.to_dict())
        
        logger.info(f"✅ اكتمل المسح: تم العثور على {len(results)} سهماً مطابقة")
        
        # تحديث الكاش
        self._cache = results
        self._last_scan = datetime.now()
        
        return results
    
    def get_summary(self, results: Optional[List[Dict]] = None) -> Dict:
        """الحصول على ملخص للنتائج"""
        target_results = results if results is not None else self._cache
        
        if not target_results or not isinstance(target_results, list):
            return {"count": 0, "avg_rsi": 0, "avg_breakout_score": 0, "trends": {}}
        
        # استخراج القيم الموثوقة واستبعاد العناصر الفاسدة إن وجدت
        valid_items = [r for r in target_results if isinstance(r, dict)]
        if not valid_items:
            return {"count": 0, "avg_rsi": 0, "avg_breakout_score": 0, "trends": {}}

        rsi_values = [float(r.get("rsi", 0) or 0) for r in valid_items]
        breakout_scores = [float(r.get("breakout_score", 0) or 0) for r in valid_items]
        
        trends = {}
        for r in valid_items:
            trend = str(r.get("trend", "غير معروف") or "غير معروف")
            trends[trend] = trends.get(trend, 0) + 1
        
        return {
            "count": len(valid_items),
            "avg_rsi": round(sum(rsi_values) / len(rsi_values), 2) if rsi_values else 0,
            "avg_breakout_score": round(sum(breakout_scores) / len(breakout_scores), 2) if breakout_scores else 0,
            "min_rsi": min(rsi_values) if rsi_values else 0,
            "max_rsi": max(rsi_values) if rsi_values else 0,
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
    if df is None or df.empty:
        return pd.DataFrame()
        
    try:
        scanner = BreakoutScanner()
        results = []
        
        res = scanner.analyze(df)
        if res and isinstance(res, tuple) and len(res) == 2:
            is_breakout, indicators = res
            if is_breakout and indicators:
                results.append({
                    'is_breakout': True,
                    'score': getattr(indicators, 'score', 0),
                    'squeeze': getattr(indicators, 'is_squeeze', False),
                    'volume_ratio': getattr(indicators, 'volume_ratio', 1.0),
                    'rsi': getattr(indicators, 'rsi', 50.0),
                    'entry': getattr(indicators, 'entry_point', 0.0),
                    'stop_loss': getattr(indicators, 'stop_loss', 0.0),
                    'target_1': getattr(indicators, 'target_1', 0.0),
                    'target_2': getattr(indicators, 'target_2', 0.0)
                })
        
        return pd.DataFrame(results)
    except Exception as e:
        logger.error(f"⚠️ خطأ في scan_from_dataframe: {e}")
        return pd.DataFrame()
