# backend/scanner/ai_breakout_analyzer.py
"""
محلل الانفجار السعري بالذكاء الاصطناعي
يكتشف أسهم الضغط ويحللها باستخدام نماذج تعلم الآلة
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# استيراد مكتبات الذكاء الاصطناعي
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    import joblib
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ مكتبات الذكاء الاصطناعي غير مثبتة. قم بتشغيل: pip install scikit-learn joblib")

# استيراد yfinance لجلب البيانات
import yfinance as yf


# ============================================================================
# نماذج البيانات
# ============================================================================

@dataclass
class SqueezeStock:
    """بيانات سهم تحت الضغط"""
    symbol: str
    name: str
    sector: str
    current_price: float
    squeeze_score: float  # درجة الضغط 0-100
    breakout_probability: float  # احتمالية الانفجار 0-1
    expected_upside: float  # النسبة المتوقعة للصعود
    risk_level: str  # 'منخفض', 'متوسط', 'مرتفع'
    time_to_breakout: str  # 'قريباً', 'خلال أيام', 'أسبوع'
    indicators: Dict = field(default_factory=dict)
    ai_prediction: Dict = field(default_factory=dict)
    entry_points: Dict = field(default_factory=dict)
    timestamp: datetime = datetime.now()
    
    def to_dict(self) -> Dict:
        data = {
            'symbol': self.symbol,
            'name': self.name,
            'sector': self.sector,
            'current_price': self.current_price,
            'squeeze_score': self.squeeze_score,
            'breakout_probability': self.breakout_probability,
            'expected_upside': self.expected_upside,
            'risk_level': self.risk_level,
            'time_to_breakout': self.time_to_breakout,
            'indicators': self.indicators,
            'ai_prediction': self.ai_prediction,
            'entry_points': self.entry_points,
            'timestamp': self.timestamp.isoformat()
        }
        return data


# ============================================================================
# جامع الأسهم الأمريكية
# ============================================================================

class USStockCollector:
    """
    جامع أسهم السوق الأمريكي
    يجلب قائمة بالأسهم المتداولة ويصنفها حسب القطاعات
    """
    
    def __init__(self):
        # قائمة موسعة للأسهم الأمريكية (S&P 500 + NASDAQ 100)
        self.stock_universe = {
            # التكنولوجيا
            'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corp.', 'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.', 'NVDA': 'NVIDIA Corp.', 'META': 'Meta Platforms',
            'TSLA': 'Tesla Inc.', 'AMD': 'Advanced Micro Devices', 'INTC': 'Intel Corp.',
            'NFLX': 'Netflix Inc.', 'PYPL': 'PayPal Holdings', 'ADBE': 'Adobe Inc.',
            'CRM': 'Salesforce Inc.', 'ORCL': 'Oracle Corp.', 'IBM': 'IBM Corp.',
            'CSCO': 'Cisco Systems', 'QCOM': 'Qualcomm Inc.', 'TXN': 'Texas Instruments',
            'AVGO': 'Broadcom Inc.', 'INTU': 'Intuit Inc.', 'AMAT': 'Applied Materials',
            'LRCX': 'Lam Research', 'MU': 'Micron Technology', 'NOW': 'ServiceNow',
            'PANW': 'Palo Alto Networks', 'SNPS': 'Synopsys Inc.', 'CDNS': 'Cadence Design',
            'MCHP': 'Microchip Technology', 'ADI': 'Analog Devices', 'NXPI': 'NXP Semiconductors',
            
            # المالية
            'JPM': 'JPMorgan Chase', 'BAC': 'Bank of America', 'WFC': 'Wells Fargo',
            'C': 'Citigroup Inc.', 'GS': 'Goldman Sachs', 'MS': 'Morgan Stanley',
            'V': 'Visa Inc.', 'MA': 'Mastercard Inc.', 'AXP': 'American Express',
            'BLK': 'BlackRock Inc.', 'SCHW': 'Charles Schwab',
            
            # الرعاية الصحية
            'JNJ': 'Johnson & Johnson', 'UNH': 'UnitedHealth', 'PFE': 'Pfizer Inc.',
            'ABBV': 'AbbVie Inc.', 'MRK': 'Merck & Co.', 'TMO': 'Thermo Fisher',
            'ABT': 'Abbott Laboratories', 'DHR': 'Danaher Corp.', 'LLY': 'Eli Lilly',
            'AMGN': 'Amgen Inc.', 'GILD': 'Gilead Sciences', 'BMY': 'Bristol-Myers',
            
            # الاستهلاك
            'WMT': 'Walmart Inc.', 'PG': 'Procter & Gamble', 'KO': 'Coca-Cola Co.',
            'PEP': 'PepsiCo Inc.', 'COST': 'Costco Wholesale', 'MCD': 'McDonald\'s Corp.',
            'NKE': 'Nike Inc.', 'SBUX': 'Starbucks Corp.', 'HD': 'Home Depot',
            'LOW': 'Lowe\'s Companies',
            
            # الطاقة والصناعة
            'XOM': 'Exxon Mobil', 'CVX': 'Chevron Corp.', 'COP': 'ConocoPhillips',
            'BA': 'Boeing Co.', 'CAT': 'Caterpillar Inc.', 'GE': 'General Electric',
            'HON': 'Honeywell International', 'LMT': 'Lockheed Martin',
            'RTX': 'Raytheon Technologies', 'UPS': 'United Parcel Service',
            
            # الاتصالات
            'T': 'AT&T Inc.', 'VZ': 'Verizon Communications', 'TMUS': 'T-Mobile US',
            'CHTR': 'Charter Communications',
            
            # العقارات
            'AMT': 'American Tower', 'PLD': 'Prologis Inc.', 'CCI': 'Crown Castle',
            'EQIX': 'Equinix Inc.', 'PSA': 'Public Storage',
            
            # المرافق
            'NEE': 'NextEra Energy', 'DUK': 'Duke Energy', 'SO': 'Southern Company',
            'D': 'Dominion Energy', 'EXC': 'Exelon Corp.'
        }
    
    def get_all_stocks(self) -> Dict[str, str]:
        """الحصول على جميع الأسهم"""
        return self.stock_universe
    
    def get_stocks_by_sector(self, sector: str) -> Dict[str, str]:
        """الحصول على أسهم قطاع محدد"""
        sector_mapping = {
            'التكنولوجيا': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 
                           'AMD', 'INTC', 'NFLX', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM',
                           'CSCO', 'QCOM', 'TXN', 'AVGO', 'INTU', 'AMAT', 'LRCX', 'MU',
                           'NOW', 'PANW', 'SNPS', 'CDNS', 'MCHP', 'ADI', 'NXPI'],
            'المالية': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'V', 'MA', 'AXP', 'BLK', 'SCHW'],
            'الرعاية الصحية': ['JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 
                              'LLY', 'AMGN', 'GILD', 'BMY'],
            'الاستهلاك': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'MCD', 'NKE', 'SBUX', 'HD', 'LOW'],
            'الطاقة': ['XOM', 'CVX', 'COP', 'BA', 'CAT', 'GE', 'HON', 'LMT', 'RTX', 'UPS'],
            'الاتصالات': ['T', 'VZ', 'TMUS', 'CHTR'],
            'العقارات': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA'],
            'المرافق': ['NEE', 'DUK', 'SO', 'D', 'EXC']
        }
        
        if sector in sector_mapping:
            return {sym: self.stock_universe[sym] for sym in sector_mapping[sector] 
                    if sym in self.stock_universe}
        return {}


# ============================================================================
# محلل الضغط والانفجار بالذكاء الاصطناعي
# ============================================================================

class AIBreakoutAnalyzer:
    """
    محلل الانفجار السعري بالذكاء الاصطناعي
    يستخدم نماذج تعلم الآلة للتنبؤ بالانفجارات
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.features = [
            'bb_bandwidth', 'bb_position', 'rsi', 'volume_ratio',
            'atr_ratio', 'price_position', 'macd_signal', 'obv_trend',
            'vwap_position', 'resistance_distance', 'support_distance',
            'volatility_ratio', 'trend_strength'
        ]
        self._init_model()
    
    def _init_model(self):
        """تهيئة نموذج الذكاء الاصطناعي"""
        if AI_AVAILABLE:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                class_weight='balanced'
            )
            # تدريب النموذج على بيانات محاكاة
            self._train_on_synthetic_data()
    
    def _train_on_synthetic_data(self):
        """تدريب النموذج على بيانات محاكاة"""
        # إنشاء بيانات تدريب محاكاة
        np.random.seed(42)
        n_samples = 1000
        
        X = np.random.randn(n_samples, len(self.features))
        # محاكاة العلاقات
        y = np.zeros(n_samples)
        for i in range(n_samples):
            # الضغط + حجم مرتفع + RSI مناسب = انفجار
            squeeze = X[i, 0] > 0.5
            volume = X[i, 2] > 0.6
            rsi = 0.3 < X[i, 1] < 0.7
            if squeeze and volume and rsi:
                y[i] = 1
            # إضافة بعض العشوائية
            elif np.random.random() > 0.95:
                y[i] = 1
        
        self.model.fit(X, y)
        self.scaler.fit(X)
        print("✅ تم تدريب نموذج الذكاء الاصطناعي")
    
    def _calculate_features(self, df: pd.DataFrame) -> np.ndarray:
        """حساب الميزات للتحليل"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        features = {}
        
        # 1. Bollinger Bands
        sma_20 = close.rolling(20).mean()
        std_20 = close.rolling(20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        features['bb_bandwidth'] = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma_20.iloc[-1]
        features['bb_position'] = (close.iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        # 2. RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
        loss = loss.replace(0, np.nan)
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        features['rsi'] = rsi.iloc[-1] / 100
        
        # 3. حجم التداول
        avg_volume = volume.iloc[-21:-1].mean()
        features['volume_ratio'] = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
        
        # 4. ATR
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean()
        features['atr_ratio'] = atr.iloc[-1] / close.iloc[-1]
        
        # 5. موقع السعر
        high_52 = high.iloc[-252:].max()
        features['price_position'] = close.iloc[-1] / high_52
        
        # 6. MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        features['macd_signal'] = 1 if macd.iloc[-1] > signal.iloc[-1] else 0
        
        # 7. OBV
        obv = (np.sign(close.diff()) * volume).cumsum()
        obv_ma = obv.rolling(20).mean()
        features['obv_trend'] = 1 if obv.iloc[-1] > obv_ma.iloc[-1] else 0
        
        # 8. VWAP
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        features['vwap_position'] = close.iloc[-1] / vwap.iloc[-1]
        
        # 9. مستويات الدعم والمقاومة
        resistance = high.iloc[-20:].max()
        support = low.iloc[-20:].min()
        features['resistance_distance'] = (resistance - close.iloc[-1]) / close.iloc[-1]
        features['support_distance'] = (close.iloc[-1] - support) / close.iloc[-1]
        
        # 10. التقلبات
        volatility = close.pct_change().rolling(20).std()
        features['volatility_ratio'] = volatility.iloc[-1] / volatility.iloc[-20:].mean()
        
        # 11. قوة الاتجاه
        sma_50 = close.rolling(50).mean()
        features['trend_strength'] = (close.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1]
        
        # تحويل إلى مصفوفة بالترتيب
        feature_values = [features.get(f, 0) for f in self.features]
        return np.array(feature_values).reshape(1, -1)
    
    def analyze_stock(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        تحليل سهم باستخدام الذكاء الاصطناعي
        
        Returns:
            قاموس بالنتائج
        """
        if len(df) < 50:
            return {'error': 'بيانات غير كافية'}
        
        try:
            # حساب الميزات
            features = self._calculate_features(df)
            
            # تطبيع الميزات
            features_scaled = self.scaler.transform(features)
            
            # التنبؤ
            if self.model is not None:
                prob = self.model.predict_proba(features_scaled)[0]
                breakout_prob = float(prob[1])
                prediction = int(self.model.predict(features_scaled)[0])
            else:
                breakout_prob = 0.5
                prediction = 0
            
            # حساب المؤشرات الإضافية
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            # درجة الضغط
            sma_20 = close.rolling(20).mean()
            std_20 = close.rolling(20).std()
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)
            bandwidth = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma_20.iloc[-1]
            
            # حساب أدنى عرض نطاق
            min_bandwidth = (bb_upper.iloc[-50:-1] - bb_lower.iloc[-50:-1]) / sma_20.iloc[-50:-1]
            min_bandwidth = min_bandwidth.min()
            
            squeeze_score = max(0, 100 - (bandwidth / min_bandwidth * 50)) if min_bandwidth > 0 else 0
            squeeze_score = min(100, squeeze_score * 2)
            
            # حجم التداول
            avg_volume = volume.iloc[-21:-1].mean()
            volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
            
            # RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0.0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
            loss = loss.replace(0, np.nan)
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_value = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # مستويات الدخول
            resistance = high.iloc[-20:].max()
            support = low.iloc[-20:].min()
            current_price = close.iloc[-1]
            
            # حساب ATR
            high_low = high - low
            high_close = abs(high - close.shift())
            low_close = abs(low - close.shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            
            entry_point = resistance + (atr * 0.3)
            stop_loss = support - (atr * 0.5)
            target_1 = entry_point + (atr * 2)
            target_2 = entry_point + (atr * 3.5)
            
            # تقدير العائد المتوقع
            expected_upside = ((target_1 - current_price) / current_price) * 100
            
            # مستوى المخاطرة
            if squeeze_score > 70 and breakout_prob > 0.7:
                risk_level = "منخفض"
            elif squeeze_score > 50 and breakout_prob > 0.5:
                risk_level = "متوسط"
            else:
                risk_level = "مرتفع"
            
            # تقدير وقت الانفجار
            if squeeze_score > 75 and volume_ratio > 1.5:
                time_to_breakout = "قريباً (خلال ساعات)"
            elif squeeze_score > 60:
                time_to_breakout = "خلال أيام"
            else:
                time_to_breakout = "أسبوع أو أكثر"
            
            return {
                'squeeze_score': round(squeeze_score, 2),
                'breakout_probability': round(breakout_prob * 100, 2),
                'prediction': 'انفجار محتمل' if prediction == 1 else 'لا يوجد انفجار',
                'expected_upside': round(expected_upside, 2),
                'risk_level': risk_level,
                'time_to_breakout': time_to_breakout,
                'indicators': {
                    'rsi': round(rsi_value, 2),
                    'volume_ratio': round(volume_ratio, 2),
                    'bandwidth': round(bandwidth, 4),
                    'price_position': round((current_price / high.iloc[-252:].max()) * 100, 2)
                },
                'entry_points': {
                    'current_price': round(current_price, 2),
                    'entry_point': round(entry_point, 2),
                    'stop_loss': round(stop_loss, 2),
                    'target_1': round(target_1, 2),
                    'target_2': round(target_2, 2)
                },
                'features': {f: round(float(v), 4) for f, v in zip(self.features, features[0])}
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def scan_universe(self, stocks: Dict[str, str], 
                     min_squeeze: float = 60,
                     min_probability: float = 60) -> List[SqueezeStock]:
        """
        مسح جميع الأسهم والعثور على مرشحي الانفجار
        
        Args:
            stocks: قاموس {symbol: name}
            min_squeeze: الحد الأدنى لدرجة الضغط
            min_probability: الحد الأدنى لاحتمالية الانفجار
        
        Returns:
            قائمة بالأسهم المرشحة
        """
        results = []
        
        for symbol, name in stocks.items():
            try:
                print(f"🔍 تحليل {symbol}...")
                
                # جلب البيانات
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="6mo")
                
                if df.empty or len(df) < 50:
                    continue
                
                # تحليل السهم
                analysis = self.analyze_stock(symbol, df)
                
                if 'error' in analysis:
                    continue
                
                # التحقق من الشروط
                if (analysis['squeeze_score'] >= min_squeeze and 
                    analysis['breakout_probability'] >= min_probability):
                    
                    # الحصول على معلومات إضافية
                    info = ticker.info
                    sector = info.get('sector', 'غير معروف')
                    
                    stock = SqueezeStock(
                        symbol=symbol,
                        name=name,
                        sector=sector,
                        current_price=analysis['entry_points']['current_price'],
                        squeeze_score=analysis['squeeze_score'],
                        breakout_probability=analysis['breakout_probability'] / 100,
                        expected_upside=analysis['expected_upside'],
                        risk_level=analysis['risk_level'],
                        time_to_breakout=analysis['time_to_breakout'],
                        indicators=analysis['indicators'],
                        ai_prediction=analysis,
                        entry_points=analysis['entry_points']
                    )
                    
                    results.append(stock)
                    
            except Exception as e:
                print(f"⚠️ خطأ في تحليل {symbol}: {e}")
                continue
        
        # ترتيب النتائج حسب الدرجة
        results.sort(key=lambda x: x.squeeze_score + (x.breakout_probability * 50), reverse=True)
        return results


# ============================================================================
# واجهة الاستخدام
# ============================================================================

class BreakoutScannerAI:
    """
    الواجهة الرئيسية للماسح الذكي بالذكاء الاصطناعي
    """
    
    def __init__(self):
        self.collector = USStockCollector()
        self.analyzer = AIBreakoutAnalyzer()
    
    def scan_market(self, sector: str = None, 
                   min_squeeze: float = 60,
                   min_probability: float = 60,
                   max_results: int = 20) -> pd.DataFrame:
        """
        مسح السوق والعثور على أفضل فرص الانفجار
        
        Args:
            sector: القطاع (اختياري)
            min_squeeze: الحد الأدنى لدرجة الضغط
            min_probability: الحد الأدنى لاحتمالية الانفجار
            max_results: الحد الأقصى للنتائج
        
        Returns:
            DataFrame بالنتائج
        """
        # الحصول على الأسهم
        if sector:
            stocks = self.collector.get_stocks_by_sector(sector)
        else:
            stocks = self.collector.get_all_stocks()
        
        print(f"📊 جاري مسح {len(stocks)} سهماً...")
        
        # مسح الأسهم
        results = self.analyzer.scan_universe(
            stocks, 
            min_squeeze=min_squeeze,
            min_probability=min_probability
        )
        
        # تحويل إلى DataFrame
        if results:
            df = pd.DataFrame([s.to_dict() for s in results[:max_results]])
            
            # اختيار الأعمدة المناسبة
            display_cols = ['symbol', 'name', 'sector', 'current_price', 
                          'squeeze_score', 'breakout_probability', 
                          'expected_upside', 'risk_level', 'time_to_breakout']
            
            df = df[display_cols]
            df['breakout_probability'] = (df['breakout_probability'] * 100).round(2)
            
            return df
        
        return pd.DataFrame()
    
    def get_top_opportunities(self, limit: int = 10) -> pd.DataFrame:
        """الحصول على أفضل الفرص"""
        return self.scan_market(max_results=limit)
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """تحليل سهم محدد بالذكاء الاصطناعي"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            
            if df.empty:
                return {'error': f'لا توجد بيانات للسهم {symbol}'}
            
            analysis = self.analyzer.analyze_stock(symbol, df)
            
            # إضافة معلومات الشركة
            info = ticker.info
            analysis['company_name'] = info.get('longName', symbol)
            analysis['sector'] = info.get('sector', 'غير معروف')
            analysis['industry'] = info.get('industry', 'غير معروف')
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}


# ============================================================================
# مثال للاستخدام
# ============================================================================

if __name__ == "__main__":
    print("🚀 تشغيل الماسح الذكي بالذكاء الاصطناعي...")
    
    # إنشاء الماسح
    scanner = BreakoutScannerAI()
    
    # مسح السوق
    print("\n📊 مسح السوق الأمريكي...")
    results = scanner.scan_market(min_squeeze=60, min_probability=55)
    
    if not results.empty:
        print("\n🔥 أفضل فرص الانفجار:")
        print(results.to_string(index=False))
    else:
        print("❌ لا توجد فرص حالياً")
    
    # تحليل سهم محدد
    print("\n📈 تحليل مفصل لسهم AAPL:")
    analysis = scanner.analyze_symbol('AAPL')
    for key, value in analysis.items():
        if key != 'features':
            print(f"{key}: {value}")
