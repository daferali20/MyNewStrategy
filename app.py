# frontend/app.py
"""
التطبيق الرئيسي للماسح الضوئي للأسهم
واجهة متكاملة مع شريط جانبي وعرض ملفات وتحليل بالذكاء الاصطناعي
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# إعدادات الصفحة
# ============================================================================

st.set_page_config(
    page_title="الماسح الضوئي للأسهم | Breakout Scanner AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة المجلد الرئيسي للمشروع للمسارات
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================================================
# استيراد الموديولات الداخلية
# ============================================================================

try:
    from backend.scanner.ai_breakout_analyzer import (
        AIBreakoutAnalyzer,
        BreakoutScannerAI,
        SqueezeStock,
        USStockCollector
    )
    from backend.scanner.breakout_scanner import BreakoutScanner, BreakoutIndicators
    from backend.scanner.screener import SmartScanner
    from backend.scanner.intraday_scanner import IntradayScanner
    AI_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ بعض الموديولات غير متوفرة: {e}")
    AI_AVAILABLE = False

# ============================================================================
# وظائف مساعدة لعرض الملفات
# ============================================================================

def get_file_content(filename):
    """جلب محتوى الملفات الفعلية من المجلدات"""
    file_paths = {
        "__init__.py": "backend/scanner/__init__.py",
        "breakout_scanner.py": "backend/scanner/breakout_scanner.py",
        "screener.py": "backend/scanner/screener.py",
        "intraday_scanner.py": "backend/scanner/intraday_scanner.py",
        "ai_breakout_analyzer.py": "backend/scanner/ai_breakout_analyzer.py",
        "market_data.py": "backend/data_providers/market_data.py",
        "technical.py": "backend/analysis/technical.py",
        "app.py": "frontend/app.py",
        "dashboard.py": "frontend/dashboard.py"
    }
    
    if filename in file_paths:
        file_path = os.path.join(ROOT_DIR, file_paths[filename])
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return f"⚠️ لا يمكن قراءة الملف: {filename}"
    
    # محتوى افتراضي للملفات غير الموجودة
    default_content = {
        "__init__.py": '''# backend/scanner/__init__.py
"""
وحدة المسح الضوئي للأسهم
"""

from .breakout_scanner import BreakoutScanner, BreakoutIndicators
from .screener import SmartScanner
from .intraday_scanner import IntradayScanner
from .ai_breakout_analyzer import AIBreakoutAnalyzer

__all__ = [
    'BreakoutScanner',
    'BreakoutIndicators',
    'SmartScanner',
    'IntradayScanner',
    'AIBreakoutAnalyzer'
]
''',
        "breakout_scanner.py": '''# backend/scanner/breakout_scanner.py
"""
ماسح الانفجار السعري
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class BreakoutIndicators:
    is_squeeze: bool
    bandwidth: float
    volume_ratio: float
    rsi: float
    score: float
    entry_point: float
    stop_loss: float
    target_1: float
    target_2: float

class BreakoutScanner:
    def __init__(self, squeeze_threshold=1.20, volume_threshold=2.0):
        self.squeeze_threshold = squeeze_threshold
        self.volume_threshold = volume_threshold
    
    def analyze(self, df):
        # تحليل الانفجار السعري
        pass
''',
        "screener.py": '''# backend/scanner/screener.py
"""
الماسح الذكي للأسهم
"""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class ScanResult:
    symbol: str
    close: float
    rsi: float
    trend: str
    score: float

class SmartScanner:
    def __init__(self, symbols):
        self.symbols = symbols
    
    def scan_market(self):
        # مسح السوق
        pass
''',
        "intraday_scanner.py": '''# backend/scanner/intraday_scanner.py
"""
الماسح الداخلي اليومي
"""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class IntradaySignal:
    symbol: str
    timeframe: str
    breakout_price: float
    volume_surge: float
    score: float

class IntradayScanner:
    def analyze(self, df):
        # تحليل داخل اليوم
        pass
''',
        "ai_breakout_analyzer.py": '''# backend/scanner/ai_breakout_analyzer.py
"""
محلل الانفجار بالذكاء الاصطناعي
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier

class AIBreakoutAnalyzer:
    def __init__(self):
        self.model = RandomForestClassifier()
    
    def analyze_stock(self, symbol, df):
        # تحليل بالذكاء الاصطناعي
        pass
    
    def scan_universe(self, stocks):
        # مسح جميع الأسهم
        pass
'''
    }
    
    return default_content.get(filename, f"📝 الملف {filename} غير موجود")
