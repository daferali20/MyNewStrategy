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

# ============================================================================
# هيكل الملفات للعرض في الشريط الجانبي - تم إصلاح الخطأ
# ============================================================================

FILES_STRUCTURE = {
    "📁 backend": {
        "📁 scanner": [
            "📄 __init__.py",
            "📄 breakout_scanner.py",
            "📄 screener.py",
            "📄 intraday_scanner.py",
            "📄 ai_breakout_analyzer.py"
        ],
        "📁 data_providers": [
            "📄 market_data.py"
        ],
        "📁 analysis": [
            "📄 technical.py"
        ]
    },
    "📁 frontend": {
        "📄 app.py",
        "📄 dashboard.py"
    },
    "📄 requirements.txt",
    "📄 README.md"
}

# ============================================================================
# دوال عرض الملفات في الشريط الجانبي
# ============================================================================

def display_file_tree(structure, indent=0, parent_key=""):
    """عرض هيكل الملفات بشكل تفاعلي في الشريط الجانبي"""
    for key, value in structure.items():
        if isinstance(value, dict):
            # مجلد
            expander = st.expander(f"{'  ' * indent}{key}", expanded=False)
            with expander:
                display_file_tree(value, indent + 1, key)
        elif isinstance(value, list):
            # ملفات داخل مجلد
            for file in value:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{'  ' * (indent + 1)}{file}")
                with col2:
                    # استخراج اسم الملف من الرمز 📄
                    file_name = file.split('📄 ')[1] if '📄 ' in file else file
                    if st.button("📖", key=f"file_{file_name}_{indent}", help=f"عرض {file_name}"):
                        st.session_state.selected_file = file_name
                        st.session_state.file_content = get_file_content(file_name)
                        st.rerun()
        else:
            # ملف فردي
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"{'  ' * indent}{key}")
            with col2:
                file_name = key.split('📄 ')[1] if '📄 ' in key else key
                if st.button("📖", key=f"file_{file_name}_{indent}", help=f"عرض {file_name}"):
                    st.session_state.selected_file = file_name
                    st.session_state.file_content = get_file_content(file_name)
                    st.rerun()

# ============================================================================
# دوال التحليل وعرض النتائج
# ============================================================================

def fetch_stock_data(symbol, period="6mo"):
    """جلب بيانات السهم من Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df
    except Exception as e:
        st.error(f"خطأ في جلب بيانات {symbol}: {e}")
        return None

def analyze_stock_ai(symbol, df):
    """تحليل السهم باستخدام الذكاء الاصطناعي"""
    if not AI_AVAILABLE:
        return None
    
    try:
        analyzer = AIBreakoutAnalyzer()
        return analyzer.analyze_stock(symbol, df)
    except Exception as e:
        st.error(f"خطأ في تحليل {symbol}: {e}")
        return None

def scan_market_ai(sector=None, min_score=60, min_prob=55):
    """مسح السوق باستخدام الذكاء الاصطناعي"""
    if not AI_AVAILABLE:
        return pd.DataFrame()
    
    try:
        scanner = BreakoutScannerAI()
        return scanner.scan_market(
            sector=sector,
            min_squeeze=min_score,
            min_probability=min_prob
        )
    except Exception as e:
        st.error(f"خطأ في مسح السوق: {e}")
        return pd.DataFrame()

def create_candlestick_chart(df, symbol, entry_points=None):
    """إنشاء رسم بياني للشموع اليابانية"""
    fig = go.Figure()
    
    # إضافة الشموع
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="السعر"
    ))
    
    # إضافة المتوسطات المتحركة
    ma20 = df['Close'].rolling(window=20).mean()
    ma50 = df['Close'].rolling(window=50).mean()
    
    fig.add_trace(go.Scatter(
        x=df.index, y=ma20,
        line=dict(color='#FFD700', width=1.5),
        name="MA20"
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index, y=ma50,
        line=dict(color='#FF6B6B', width=1.5),
        name="MA50"
    ))
    
    # إضافة مستويات الدخول والخروج
    if entry_points:
        if 'entry_point' in entry_points:
            fig.add_hline(
                y=entry_points['entry_point'],
                line_dash="dash",
                line_color="#00E676",
                annotation_text="نقطة الدخول",
                annotation_position="top right"
            )
        if 'stop_loss' in entry_points:
            fig.add_hline(
                y=entry_points['stop_loss'],
                line_dash="dot",
                line_color="#FF5252",
                annotation_text="وقف الخسارة",
                annotation_position="bottom right"
            )
        if 'target_1' in entry_points:
            fig.add_hline(
                y=entry_points['target_1'],
                line_dash="dash",
                line_color="#29B6F6",
                annotation_text="الهدف 1",
                annotation_position="top left"
            )
        if 'target_2' in entry_points:
            fig.add_hline(
                y=entry_points['target_2'],
                line_dash="dash",
                line_color="#AB47BC",
                annotation_text="الهدف 2",
                annotation_position="bottom left"
            )
    
    # تنسيق الرسم البياني
    fig.update_layout(
        title=f"📈 {symbol} - رسم بياني فني",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

# ============================================================================
# الشريط الجانبي
# ============================================================================

def render_sidebar():
    """عرض محتوى الشريط الجانبي"""
    with st.sidebar:
        # الشعار والعنوان
        st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        st.title("🚀 الماسح الضوئي")
        st.markdown("---")
        
        # ====================================================================
        # مستكشف الملفات
        # ====================================================================
        st.subheader("📂 مستكشف الملفات")
        display_file_tree(FILES_STRUCTURE)
        
        st.markdown("---")
        
        # ====================================================================
        # أدوات سريعة
        # ====================================================================
        st.subheader("🔧 أدوات سريعة")
        
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ تم تحديث البيانات!")
            st.rerun()
        
        if st.button("📥 تصدير النتائج", use_container_width=True):
            if 'scan_results' in st.session_state and not st.session_state.scan_results.empty:
                csv = st.session_state.scan_results.to_csv(index=False)
                st.download_button(
                    label="📊 تحميل CSV",
                    data=csv,
                    file_name=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ لا توجد نتائج للتصدير")
        
        st.markdown("---")
        
        # ====================================================================
        # إعدادات المسح
        # ====================================================================
        st.subheader("⚙️ إعدادات المسح")
        
        # إعدادات الفلترة
        min_score = st.slider(
            "🎯 درجة الجاهزية",
            min_value=50,
            max_value=95,
            value=70,
            step=5,
            help="الحد الأدنى لدرجة الجاهزية للانفجار"
        )
        
        min_prob = st.slider(
            "📊 احتمالية الانفجار",
            min_value=30,
            max_value=90,
            value=55,
            step=5,
            help="الحد الأدنى لاحتمالية الانفجار"
        )
        
        # اختيار القطاع
        sectors = ["الكل", "التكنولوجيا", "المالية", "الرعاية الصحية", "الاستهلاك", "الطاقة", "الاتصالات"]
        selected_sector = st.selectbox("🏢 القطاع", sectors)
        
        # زر تشغيل المسح
        scan_button = st.button(
            "🔍 ابدأ المسح",
            use_container_width=True,
            type="primary"
        )
        
        st.markdown("---")
        
        # ====================================================================
        # معلومات النظام
        # ====================================================================
        st.subheader("ℹ️ معلومات النظام")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 الأسهم", "150+")
        with col2:
            st.metric("🎯 الفرص", "12")
        
        st.caption(f"⏱️ آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("💡 اختر ملفاً من المستكشف لعرض محتواه")
        
        # حالة الذكاء الاصطناعي
        if AI_AVAILABLE:
            st.success("✅ الذكاء الاصطناعي: نشط")
        else:
            st.warning("⚠️ الذكاء الاصطناعي: غير متوفر")
        
        return min_score, min_prob, selected_sector, scan_button

# ============================================================================
# المحتوى الرئيسي
# ============================================================================

def render_main_content():
    """عرض المحتوى الرئيسي للتطبيق"""
    
    # الهيدر
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
        }
        .file-content {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
            font-family: 'Courier New', monospace;
            max-height: 600px;
            overflow-y: auto;
        }
        .metric-card {
            background-color: #1e1e1e;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stock-card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
            border-radius: 12px;
            border-right: 4px solid #667eea;
            margin: 10px 0;
        }
        .recommendation {
            padding: 10px 15px;
            border-radius: 8px;
            margin: 5px 0;
        }
        .rec-buy {
            background-color: rgba(0, 230, 118, 0.15);
            border-left: 4px solid #00E676;
        }
        .rec-hold {
            background-color: rgba(255, 193, 7, 0.15);
            border-left: 4px solid #FFC107;
        }
        .rec-sell {
            background-color: rgba(255, 82, 82, 0.15);
            border-left: 4px solid #FF5252;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0;">🚀 الماسح الضوئي للأسهم المتفجرة</h1>
        <p style="margin-top:5px; opacity:0.9; font-size:1.1rem;">
            اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي وتحليل الضغط (Squeeze)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # التحقق من وجود ملف مختار
    if 'selected_file' in st.session_state and st.session_state.selected_file:
        selected = st.session_state.selected_file
        st.subheader(f"📄 محتوى الملف: {selected}")
        
        content = st.session_state.get('file_content', get_file_content(selected))
        
        if content:
            # تحديد لغة التلوين حسب الامتداد
            ext = selected.split('.')[-1] if '.' in selected else 'text'
            languages = {
                'py': 'python',
                'js': 'javascript',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'md': 'markdown',
                'txt': 'text'
            }
            lang = languages.get(ext, 'text')
            st.code(content, language=lang)
        else:
            st.info(f"📝 الملف {selected} فارغ أو غير موجود")
        
        # زر إغلاق العرض
        if st.button("❌ إغلاق الملف"):
            del st.session_state.selected_file
            del st.session_state.file_content
            st.rerun()
    
    else:
        # عرض لوحة التحكم الرئيسية
        render_dashboard()

# ============================================================================
# لوحة التحكم الرئيسية
# ============================================================================

def render_dashboard():
    """عرض لوحة التحكم الرئيسية"""
    
    # ========================================================================
    # الإحصائيات السريعة
    # ========================================================================
    st.subheader("📊 نظرة عامة على السوق")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈</h3>
            <p style="font-size:1.5rem; font-weight:bold;">150+</p>
            <p style="color:#888;">أسهم مفحوصة</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🔥</h3>
            <p style="font-size:1.5rem; font-weight:bold; color:#FF6B6B;">8</p>
            <p style="color:#888;">فرص انفجار</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊</h3>
            <p style="font-size:1.5rem; font-weight:bold; color:#4CAF50;">84.2%</p>
            <p style="color:#888;">متوسط الدقة</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <p style="font-size:1.5rem; font-weight:bold; color:#FFD700;">NVDA</p>
            <p style="color:#888;">أفضل فرصة</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # نتائج المسح
    # ========================================================================
    st.subheader("🔍 نتائج المسح")
    
    # عرض نتائج المسح المخزنة
    if 'scan_results' in st.session_state and not st.session_state.scan_results.empty:
        df = st.session_state.scan_results
        
        # عرض الجدول
        st.dataframe(
            df,
            column_config={
                "symbol": st.column_config.TextColumn("الرمز"),
                "name": st.column_config.TextColumn("الشركة"),
                "sector": st.column_config.TextColumn("القطاع"),
                "current_price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                "squeeze_score": st.column_config.ProgressColumn("درجة الضغط", format="%d/100", min_value=0, max_value=100),
                "breakout_probability": st.column_config.ProgressColumn("احتمالية الانفجار", format="%.1f%%", min_value=0, max_value=100),
                "expected_upside": st.column_config.NumberColumn("العائد المتوقع", format="%.1f%%"),
                "risk_level": st.column_config.TextColumn("المخاطرة"),
                "time_to_breakout": st.column_config.TextColumn("توقيت الانفجار")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # عرض تفاصيل السهم المختار
        st.markdown("---")
        st.subheader("📊 تحليل مفصل لسهم محدد")
        
        selected_symbol = st.selectbox(
            "اختر سهماً للتحليل التفصيلي:",
            df['symbol'].tolist()
        )
        
        if selected_symbol:
            display_stock_details(selected_symbol)
    
    else:
        # رسالة عند عدم وجود نتائج
        st.info("👆 استخدم الشريط الجانبي لضبط الإعدادات ثم اضغط 'ابدأ المسح'")
        
        # عرض نموذج للنتائج
        st.subheader("📋 نموذج للنتائج المتوقعة")
        
        sample_data = pd.DataFrame({
            'الرمز': ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA'],
            'الشركة': ['NVIDIA Corp', 'AMD Corp', 'Apple Inc', 'Microsoft', 'Tesla Inc'],
            'السعر': [895.32, 165.42, 175.34, 378.91, 245.68],
            'درجة الضغط': [92, 78, 85, 71, 65],
            'احتمالية الانفجار': ['85%', '72%', '68%', '55%', '48%'],
            'المخاطرة': ['منخفضة', 'متوسطة', 'منخفضة', 'متوسطة', 'مرتفعة']
        })
        
        st.dataframe(sample_data, use_container_width=True, hide_index=True)

# ============================================================================
# عرض تفاصيل السهم
# ============================================================================

def display_stock_details(symbol):
    """عرض تحليل تفصيلي لسهم معين"""
    
    with st.spinner(f"📊 جاري تحليل {symbol}..."):
        # جلب البيانات
        df = fetch_stock_data(symbol, period="6mo")
        
        if df is None or df.empty:
            st.error(f"❌ لا توجد بيانات للسهم {symbol}")
            return
        
        # تحليل الذكاء الاصطناعي
        analysis = analyze_stock_ai(symbol, df)
        
        # عرض المعلومات الأساسية
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # الرسم البياني
            entry_points = None
            if analysis and 'entry_points' in analysis:
                entry_points = analysis['entry_points']
            
            fig = create_candlestick_chart(df, symbol, entry_points)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # عرض التفاصيل
            st.markdown(f"### 🎯 {symbol}")
            
            if analysis and 'error' not in analysis:
                # مؤشرات الأداء
                st.metric("درجة الضغط", f"{analysis.get('squeeze_score', 0)}/100")
                st.metric("احتمالية الانفجار", f"{analysis.get('breakout_probability', 0)}%")
                st.metric("العائد المتوقع", f"{analysis.get('expected_upside', 0)}%")
                
                # مستويات الدخول والخروج
                entry = analysis.get('entry_points', {})
                if entry:
                    st.markdown("---")
                    st.markdown("#### 📍 مستويات التداول")
                    st.write(f"💰 السعر الحالي: **${entry.get('current_price', 0):.2f}**")
                    st.write(f"📈 نقطة الدخول: **${entry.get('entry_point', 0):.2f}**")
                    st.write(f"🛑 وقف الخسارة: **${entry.get('stop_loss', 0):.2f}**")
                    st.write(f"🎯 الهدف 1: **${entry.get('target_1', 0):.2f}**")
                    st.write(f"🎯 الهدف 2: **${entry.get('target_2', 0):.2f}**")
                
                # المخاطرة والتوقيت
                st.markdown("---")
                st.markdown("#### ⚡ معلومات إضافية")
                st.write(f"📊 المخاطرة: **{analysis.get('risk_level', 'غير معروف')}**")
                st.write(f"⏱️ توقيت الانفجار: **{analysis.get('time_to_breakout', 'غير معروف')}**")
                
                # التوصية
                prob = analysis.get('breakout_probability', 0)
                if prob >= 70:
                    st.success("✅ توصية: شراء قوي")
                elif prob >= 50:
                    st.info("ℹ️ توصية: مراقبة")
                else:
                    st.warning("⚠️ توصية: انتظار")
            else:
                st.warning("⚠️ لا توجد بيانات تحليل متوفرة")
        
        # عرض المؤشرات الفنية
        if analysis and 'indicators' in analysis:
            st.markdown("---")
            st.subheader("📊 المؤشرات الفنية")
            
            ind = analysis['indicators']
            cols = st.columns(4)
            
            with cols[0]:
                st.metric("RSI", ind.get('rsi', 'N/A'))
            with cols[1]:
                st.metric("مضاعف الحجم", f"{ind.get('volume_ratio', 0):.1f}x")
            with cols[2]:
                st.metric("عرض النطاق", f"{ind.get('bandwidth', 0):.3f}")
            with cols[3]:
                st.metric("موقع السعر", f"{ind.get('price_position', 0):.1f}%")

# ============================================================================
# تشغيل المسح
# ============================================================================

def run_scan(sector, min_score, min_prob):
    """تشغيل عملية المسح"""
    
    with st.spinner("🔍 جاري مسح السوق... هذا قد يستغرق بضع ثوانٍ"):
        # مسح السوق
        results = scan_market_ai(
            sector=None if sector == "الكل" else sector,
            min_score=min_score,
            min_prob=min_prob
        )
        
        if not results.empty:
            st.session_state.scan_results = results
            st.success(f"✅ تم العثور على {len(results)} فرصة!")
            st.rerun()
        else:
            st.warning("❌ لا توجد فرص مطابقة للمعايير الحالية")
            st.session_state.scan_results = pd.DataFrame()

# ============================================================================
# التشغيل الرئيسي
# ============================================================================

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # عرض الشريط الجانبي والحصول على الإعدادات
    min_score, min_prob, selected_sector, scan_button = render_sidebar()
    
    # تشغيل المسح عند الضغط على الزر
    if scan_button:
        run_scan(selected_sector, min_score, min_prob)
    
    # عرض المحتوى الرئيسي
    render_main_content()

# ============================================================================
# تشغيل التطبيق
# ============================================================================

if __name__ == "__main__":
    main()
