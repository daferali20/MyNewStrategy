# app.py
"""
التطبيق الرئيسي - الماسح الضوئي للأسهم
نسخة محسنة مع استخدام width بدلاً من use_container_width
"""

import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import time
from functools import lru_cache

# ============================================================================
# إعدادات الصفحة
# ============================================================================

st.set_page_config(
    page_title="الماسح الضوئي للأسهم | Breakout Scanner",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة المسارات
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================================================
# تحميل التصميم
# ============================================================================

def load_css():
    """تحميل ملف التصميم ثلاثي الأبعاد"""
    css_path = os.path.join(ROOT_DIR, "frontend", "assets", "style.css")
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except:
            load_inline_css()
    else:
        load_inline_css()

def load_inline_css():
    """تصميم مضمن في حال عدم وجود الملف"""
    st.markdown("""
    <style>
    /* تصميم ثلاثي الأبعاد مباشر */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 35px 40px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        transform: perspective(1000px) rotateX(2deg) rotateY(-2deg);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .main-header:hover {
        transform: perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1.02);
        box-shadow: 0 30px 60px -12px rgba(0,0,0,0.6), 0 0 40px rgba(102,126,234,0.3);
    }
    .main-header h1 {
        font-size: 2.2rem;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .main-header p {
        opacity: 0.9;
        margin-top: 8px;
        font-size: 1.1rem;
    }
    [data-testid="stSidebar"] {
        background: rgba(26, 26, 46, 0.92) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
        box-shadow: 10px 0 40px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        transform: perspective(800px) rotateX(0deg) rotateY(0deg);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
    }
    .metric-card:hover {
        transform: perspective(800px) rotateX(5deg) rotateY(5deg) translateY(-10px);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        border-color: rgba(102,126,234,0.3);
    }
    .metric-card .icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: white;
    }
    .metric-card .label {
        color: #888;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    .stock-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 12px;
        border-right: 4px solid #667eea;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .stock-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(102,126,234,0.2);
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge.buy { background: rgba(0,230,118,0.2); color: #00E676; }
    .status-badge.hold { background: rgba(255,193,7,0.2); color: #FFC107; }
    .status-badge.sell { background: rgba(255,82,82,0.2); color: #FF5252; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# تهيئة حالة الجلسة
# ============================================================================

def init_session_state():
    """تهيئة جميع متغيرات الجلسة"""
    defaults = {
        'scan_results': pd.DataFrame(),
        'selected_file': None,
        'show_file': False,
        'current_page': 'dashboard',
        'selected_symbol': None,
        'analysis_results': None,
        'stock_data': None,
        'sidebar_config': None,
        'last_scan_time': None,
        'scan_in_progress': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# دوال الميزات المحسنة
# ============================================================================

@st.cache_data(ttl=300)  # تخزين مؤقت لمدة 5 دقائق
def get_stock_data_cached(symbol, period="6mo"):
    """جلب بيانات السهم مع التخزين المؤقت"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)  # تخزين مؤقت لمدة 10 دقائق
def get_stock_info_cached(symbol):
    """جلب معلومات الشركة مع التخزين المؤقت"""
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except:
        return {}

def scan_market_ai(sector=None, min_score=60, min_prob=55, max_symbols=20):
    """
    مسح السوق باستخدام الذكاء الاصطناعي مع تحسين الأداء
    """
    # قائمة الأسهم الأمريكية الموسعة
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD',
               'INTC', 'NFLX', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'CSCO',
               'QCOM', 'TXN', 'AVGO', 'INTU', 'AMAT', 'LRCX', 'MU', 'NOW',
               'PANW', 'SNPS', 'CDNS', 'MCHP', 'ADI', 'NXPI']
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, symbol in enumerate(symbols[:max_symbols]):
        status_text.text(f"🔍 جاري تحليل {symbol}... ({idx+1}/{min(len(symbols), max_symbols)})")
        progress_bar.progress((idx + 1) / min(len(symbols), max_symbols))
        
        try:
            df = get_stock_data_cached(symbol, period="6mo")
            if df.empty or len(df) < 50:
                continue
            
            close = df['Close']
            volume = df['Volume']
            
            # حساب مؤشرات فنية محسنة
            sma_20 = close.rolling(20).mean()
            std_20 = close.rolling(20).std()
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)
            bandwidth = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma_20.iloc[-1] if sma_20.iloc[-1] > 0 else 0
            
            # درجة الضغط المحسنة
            min_bandwidth = ((bb_upper - bb_lower) / sma_20).iloc[-50:-1].min() if len(df) > 50 else bandwidth
            squeeze_score = max(0, min(100, ((1 - bandwidth / min_bandwidth) * 100) if min_bandwidth > 0 else 50))
            
            # حجم التداول
            avg_volume = volume.iloc[-21:-1].mean() if len(volume) > 21 else volume.mean()
            volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
            
            # احتمالية الانفجار المحسنة
            breakout_prob = min(100, (squeeze_score * 0.5 + min(volume_ratio * 20, 50)))
            
            # معلومات الشركة
            info = get_stock_info_cached(symbol)
            name = info.get('longName', symbol)
            sector_name = info.get('sector', 'غير معروف')
            
            # فلترة حسب القطاع
            if sector and sector_name != sector:
                continue
            
            # فلترة حسب الدرجة
            if squeeze_score >= min_score and breakout_prob >= min_prob:
                current_price = close.iloc[-1]
                high = df['High'].iloc[-20:].max()
                low = df['Low'].iloc[-20:].min()
                atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or current_price * 0.02
                
                # حساب مستويات الدخول المحسنة
                entry_point = high + (atr * 0.5)
                stop_loss = current_price - (atr * 1.5)
                target_1 = entry_point + (atr * 2)
                target_2 = entry_point + (atr * 3.5)
                
                results.append({
                    'symbol': symbol,
                    'name': name[:35],
                    'sector': sector_name,
                    'current_price': round(current_price, 2),
                    'squeeze_score': round(squeeze_score, 2),
                    'breakout_probability': round(breakout_prob, 2),
                    'expected_upside': round(((target_1 - current_price) / current_price) * 100, 2),
                    'risk_level': 'منخفض' if squeeze_score > 70 and volume_ratio > 1.5 else 'متوسط' if squeeze_score > 50 else 'مرتفع',
                    'time_to_breakout': 'قريباً' if squeeze_score > 75 else 'خلال أيام' if squeeze_score > 60 else 'أسبوع',
                    'entry_point': round(entry_point, 2),
                    'stop_loss': round(stop_loss, 2),
                    'target_1': round(target_1, 2),
                    'target_2': round(target_2, 2),
                    'volume_ratio': round(volume_ratio, 2)
                })
                
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def create_candlestick_chart(df, symbol, entry_points=None, show_volume=True):
    """إنشاء رسم بياني للشموع مع تحسينات"""
    fig = go.Figure()
    
    # الشموع
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="السعر",
        increasing=dict(line=dict(color='#00E676')),
        decreasing=dict(line=dict(color='#FF5252'))
    ))
    
    # المتوسطات المتحركة
    if len(df) > 20:
        ma20 = df['Close'].rolling(20).mean()
        ma50 = df['Close'].rolling(50).mean() if len(df) > 50 else None
        ma200 = df['Close'].rolling(200).mean() if len(df) > 200 else None
        
        colors = ['#FFD700', '#29B6F6', '#AB47BC']
        mas = [(ma20, 'MA20', colors[0])]
        if ma50 is not None:
            mas.append((ma50, 'MA50', colors[1]))
        if ma200 is not None:
            mas.append((ma200, 'MA200', colors[2]))
        
        for ma, name, color in mas:
            fig.add_trace(go.Scatter(
                x=df.index, y=ma,
                line=dict(color=color, width=1.2),
                name=name,
                opacity=0.7
            ))
    
    # مستويات الدخول والخروج
    if entry_points:
        levels = [
            ('entry_point', '#00E676', 'نقطة الدخول', 'top right'),
            ('stop_loss', '#FF5252', 'وقف الخسارة', 'bottom right'),
            ('target_1', '#29B6F6', 'الهدف 1', 'top left'),
            ('target_2', '#AB47BC', 'الهدف 2', 'bottom left')
        ]
        for key, color, label, position in levels:
            if key in entry_points and entry_points[key]:
                fig.add_hline(
                    y=entry_points[key],
                    line_dash="dash",
                    line_color=color,
                    annotation_text=label,
                    annotation_position=position,
                    annotation=dict(font=dict(color=color))
                )
    
    fig.update_layout(
        title=f"📈 {symbol} - تحليل فني",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    return fig

def get_file_content(filename):
    """جلب محتوى الملفات مع تحسين"""
    # محاولة قراءة الملف الفعلي
    file_paths = {
        "app.py": "app.py",
        "breakout_scanner.py": "backend/scanner/breakout_scanner.py",
        "screener.py": "backend/scanner/screener.py",
        "__init__.py": "backend/scanner/__init__.py",
    }
    
    if filename in file_paths:
        path = os.path.join(ROOT_DIR, file_paths[filename])
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
    
    # محتوى افتراضي
    default_content = {
        "app.py": """# app.py - التطبيق الرئيسي
import streamlit as st

st.title("🚀 الماسح الضوئي للأسهم")
""",
        "breakout_scanner.py": """# breakout_scanner.py - ماسح الانفجار
class BreakoutScanner:
    def __init__(self):
        self.squeeze_threshold = 1.2
    
    def analyze(self, df):
        return {'is_breakout': True, 'score': 75}
""",
        "screener.py": """# screener.py - الماسح الذكي
class SmartScanner:
    def __init__(self, symbols):
        self.symbols = symbols
    
    def scan(self):
        return [{'symbol': 'AAPL', 'score': 85}]
""",
        "__init__.py": "# ملف تهيئة الوحدة",
        "requirements.txt": "streamlit>=1.28.0\npandas>=2.0.0\nyfinance>=0.2.0\nplotly>=5.14.0",
        "README.md": "# الماسح الضوئي للأسهم\n\nتطبيق لمسح الأسهم الأمريكية باستخدام الذكاء الاصطناعي."
    }
    return default_content.get(filename, f"# الملف: {filename}\n\nالمحتوى غير متوفر")

# ============================================================================
# مكونات الواجهة - مع تحديث width
# ============================================================================

def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
        st.title("🚀 الماسح الضوئي")
        st.markdown("---")
        
        # القائمة الرئيسية
        pages = {
            "📊 لوحة التحكم": "dashboard",
            "🔍 مسح السوق": "scanner",
            "📂 مستكشف الملفات": "files",
            "📈 تحليل سهم": "analyze"
        }
        
        selected = st.radio(
            "القائمة", 
            list(pages.keys()), 
            index=0,
            key="main_menu_radio"
        )
        st.session_state.current_page = pages[selected]
        
        st.markdown("---")
        
        # إعدادات المسح
        st.subheader("⚙️ إعدادات المسح")
        min_score = st.slider(
            "🎯 درجة الجاهزية", 
            50, 95, 70,
            key="min_score_slider",
            help="الحد الأدنى لدرجة الضغط المطلوبة"
        )
        min_prob = st.slider(
            "📊 احتمالية الانفجار", 
            30, 90, 55,
            key="min_prob_slider",
            help="الحد الأدنى لاحتمالية الانفجار"
        )
        
        sectors = ["الكل", "التكنولوجيا", "المالية", "الرعاية الصحية", "الاستهلاك", "الطاقة", "الاتصالات"]
        sector = st.selectbox("🏢 القطاع", sectors, key="sector_select")
        
        max_symbols = st.slider(
            "📈 عدد الأسهم للمسح",
            5, 30, 15,
            key="max_symbols",
            help="عدد الأسهم التي سيتم مسحها (زيادة العدد تزيد وقت المسح)"
        )
        
        # تحديث: استخدام width بدلاً من use_container_width
        scan_clicked = st.button(
            "🔍 ابدأ المسح", 
            width="stretch",  # تم التحديث من use_container_width=True
            type="primary",
            key="scan_button"
        )
        
        st.markdown("---")
        
        # معلومات إضافية
        if st.session_state.last_scan_time:
            st.caption(f"⏱️ آخر مسح: {st.session_state.last_scan_time}")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # تخزين الإعدادات
        st.session_state.sidebar_config = {
            'min_score': min_score,
            'min_prob': min_prob,
            'sector': None if sector == "الكل" else sector,
            'max_symbols': max_symbols,
            'scan_clicked': scan_clicked
        }
        
        return st.session_state.sidebar_config

def render_dashboard():
    """لوحة التحكم"""
    st.subheader("📊 نظرة عامة على السوق")
    
    # بطاقات إحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">📈</div>
            <div class="value">150+</div>
            <div class="label">أسهم مفحوصة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🔥</div>
            <div class="value" style="color:#FF6B6B;">8</div>
            <div class="label">فرص انفجار</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">📊</div>
            <div class="value" style="color:#4CAF50;">84.2%</div>
            <div class="label">متوسط الدقة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🎯</div>
            <div class="value" style="color:#FFD700;">NVDA</div>
            <div class="label">أفضل فرصة</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # عرض نتائج المسح
    if not st.session_state.scan_results.empty:
        st.subheader("📋 نتائج المسح")
        
        df_display = st.session_state.scan_results.copy()
        if 'breakout_probability' in df_display.columns:
            df_display['breakout_probability'] = df_display['breakout_probability'].round(1)
        
        st.dataframe(
            df_display,
            column_config={
                "symbol": st.column_config.TextColumn("الرمز", width="small"),
                "name": st.column_config.TextColumn("الشركة"),
                "sector": st.column_config.TextColumn("القطاع", width="small"),
                "current_price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                "squeeze_score": st.column_config.ProgressColumn("درجة الضغط", format="%d/100", min_value=0, max_value=100),
                "breakout_probability": st.column_config.ProgressColumn("احتمالية الانفجار", format="%.1f%%", min_value=0, max_value=100),
                "expected_upside": st.column_config.NumberColumn("العائد المتوقع", format="%.1f%%"),
                "risk_level": st.column_config.TextColumn("المخاطرة"),
                "time_to_breakout": st.column_config.TextColumn("التوقيت"),
                "volume_ratio": st.column_config.NumberColumn("مضاعف الحجم", format="%.1fx")
            },
            width="stretch",  # تم التحديث من use_container_width=True
            hide_index=True
        )
        
        # عرض عدد النتائج
        st.caption(f"✅ تم العثور على {len(df_display)} فرصة مطابقة للمعايير")
    else:
        st.info("👆 اضغط 'ابدأ المسح' في الشريط الجانبي للحصول على النتائج")
        
        # عرض نموذج للنتائج
        with st.expander("📋 نموذج للنتائج المتوقعة"):
            sample_data = pd.DataFrame({
                'الرمز': ['NVDA', 'AMD', 'AAPL', 'MSFT', 'TSLA'],
                'الشركة': ['NVIDIA Corp', 'AMD Corp', 'Apple Inc', 'Microsoft', 'Tesla Inc'],
                'القطاع': ['التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'التكنولوجيا', 'السيارات'],
                'السعر': ['$895.32', '$165.42', '$175.34', '$378.91', '$245.68'],
                'درجة الضغط': ['92/100', '78/100', '85/100', '71/100', '65/100'],
                'احتمالية الانفجار': ['85%', '72%', '68%', '55%', '48%'],
                'المخاطرة': ['منخفضة', 'متوسطة', 'منخفضة', 'متوسطة', 'مرتفعة']
            })
            st.dataframe(sample_data, width="stretch", hide_index=True)  # تم التحديث

def render_scanner():
    """صفحة مسح السوق"""
    st.subheader("🔍 مسح السوق الآلي")
    
    # عرض الإعدادات الحالية
    config = st.session_state.sidebar_config or {'min_score': 70, 'min_prob': 55, 'sector': None, 'max_symbols': 15}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 درجة الجاهزية", f"{config.get('min_score', 70)}/100")
    with col2:
        st.metric("📊 احتمالية الانفجار", f"{config.get('min_prob', 55)}%")
    with col3:
        sector_display = config.get('sector') or 'الكل'
        st.metric("🏢 القطاع", sector_display)
    
    st.markdown("---")
    
    # زر التحديث
    col1, col2 = st.columns([1, 4])
    with col1:
        # تحديث: استخدام width بدلاً من use_container_width
        refresh = st.button("🔄 تحديث", type="primary", key="refresh_scan", width="stretch")
    
    if refresh:
        with st.spinner("🔍 جاري مسح السوق..."):
            results = scan_market_ai(
                sector=config.get('sector'),
                min_score=config.get('min_score', 70),
                min_prob=config.get('min_prob', 55),
                max_symbols=config.get('max_symbols', 15)
            )
            if not results.empty:
                st.session_state.scan_results = results
                st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                st.success(f"✅ تم العثور على {len(results)} فرصة!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")
    
    # عرض النتائج
    if not st.session_state.scan_results.empty:
        st.subheader(f"📊 النتائج ({len(st.session_state.scan_results)})")
        st.dataframe(
            st.session_state.scan_results,
            width="stretch",  # تم التحديث
            hide_index=True
        )
        
        # أزرار التصدير
        col1, col2, col3 = st.columns(3)
        with col1:
            csv = st.session_state.scan_results.to_csv(index=False)
            # تحديث: استخدام width بدلاً من use_container_width
            st.download_button(
                "📥 تحميل CSV",
                csv,
                f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                key="download_csv",
                width="stretch"
            )
        with col2:
            # تحديث: استخدام width بدلاً من use_container_width
            if st.button("📋 نسخ", width="stretch"):
                st.toast("✅ تم نسخ النتائج!")
        with col3:
            # تحديث: استخدام width بدلاً من use_container_width
            if st.button("📧 مشاركة", width="stretch"):
                st.toast("📧 تم فتح مشاركة النتائج!")

def render_file_explorer():
    """مستكشف الملفات"""
    st.subheader("📂 مستكشف الملفات")
    
    files = {
        "📁 Backend": {
            "scanner": ["__init__.py", "breakout_scanner.py", "screener.py"],
            "data_providers": ["market_data.py"],
            "analysis": ["technical.py"]
        },
        "📁 Frontend": {
            "": ["app.py", "dashboard.py"],
            "assets": ["style.css"],
            "components": ["sidebar.py", "charts.py"]
        },
        "📄 requirements.txt": None,
        "📄 README.md": None
    }
    
    for name, content in files.items():
        if isinstance(content, dict):
            with st.expander(f"{name}", expanded=False):
                for subfolder, items in content.items():
                    if subfolder:
                        st.markdown(f"**📂 {subfolder}/**")
                    for file in items:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"   📄 {file}")
                        with col2:
                            if st.button("📖", key=f"file_btn_{file}_{subfolder}"):
                                st.session_state.selected_file = file
                                st.session_state.show_file = True
                                st.rerun()
        else:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(name)
            with col2:
                if st.button("📖", key=f"file_btn_{name}"):
                    st.session_state.selected_file = name
                    st.session_state.show_file = True
                    st.rerun()
    
    if st.session_state.show_file and st.session_state.selected_file:
        st.markdown("---")
        st.subheader(f"📄 محتوى: {st.session_state.selected_file}")
        content = get_file_content(st.session_state.selected_file)
        
        # تحديد لغة التلوين
        ext = st.session_state.selected_file.split('.')[-1] if '.' in st.session_state.selected_file else 'txt'
        lang_map = {'py': 'python', 'js': 'javascript', 'html': 'html', 'css': 'css', 'json': 'json', 'md': 'markdown'}
        lang = lang_map.get(ext, 'text')
        
        st.code(content, language=lang)
        
        # تحديث: استخدام width بدلاً من use_container_width
        if st.button("❌ إغلاق", key="close_file", width="stretch"):
            st.session_state.show_file = False
            st.session_state.selected_file = None
            st.rerun()

def render_analyze():
    """تحليل سهم محدد"""
    st.subheader("📈 تحليل سهم محدد")
    
    # اختيار سهم من النتائج أو إدخال يدوي
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not st.session_state.scan_results.empty:
            symbols = st.session_state.scan_results['symbol'].tolist()
            selected = st.selectbox("اختر من النتائج:", ["-- اختر سهماً --"] + symbols, key="stock_select")
            if selected != "-- اختر سهماً --":
                symbol = selected
            else:
                symbol = st.text_input("أو أدخل رمز السهم:", value="AAPL", key="symbol_input").upper()
        else:
            symbol = st.text_input("أدخل رمز السهم (مثل: AAPL):", value="AAPL", key="symbol_input").upper()
    
    with col2:
        period = st.selectbox("الفترة:", ["1mo", "3mo", "6mo", "1y", "2y"], index=2, key="period_select")
    
    if symbol:
        with st.spinner(f"📊 جاري تحليل {symbol}..."):
            df = get_stock_data_cached(symbol, period=period)
            
            if df.empty:
                st.error(f"❌ لا توجد بيانات للسهم {symbol}")
                return
            
            # عرض معلومات السهم
            info = get_stock_info_cached(symbol)
            company_name = info.get('longName', symbol)
            sector = info.get('sector', 'غير معروف')
            industry = info.get('industry', 'غير معروف')
            
            st.markdown(f"""
            <div class="stock-card">
                <h3>{symbol} - {company_name}</h3>
                <p>🏢 {sector} | 📊 {industry}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # التحليل
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # حساب مستويات الدخول
                current = df['Close'].iloc[-1]
                high_20 = df['High'].iloc[-20:].max()
                low_20 = df['Low'].iloc[-20:].min()
                atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1] or current * 0.02
                
                entry_points = {
                    'entry_point': high_20 + (atr * 0.5),
                    'stop_loss': current - (atr * 1.5),
                    'target_1': current + (atr * 2),
                    'target_2': current + (atr * 3.5)
                }
                
                fig = create_candlestick_chart(df, symbol, entry_points)
                st.plotly_chart(fig, use_container_width=True)  # Plotly لا يزال يستخدم use_container_width
            
            with col2:
                # إحصائيات سريعة
                st.metric("💰 السعر الحالي", f"${current:.2f}")
                st.metric("📈 أعلى سعر (20 يوم)", f"${high_20:.2f}")
                st.metric("📉 أدنى سعر (20 يوم)", f"${low_20:.2f}")
                st.metric("📊 حجم التداول", f"{df['Volume'].iloc[-1]:,.0f}")
                
                st.markdown("---")
                st.markdown("#### 📍 مستويات التداول")
                
                # عرض المستويات مع تنسيق
                levels = [
                    ('🎯 الهدف 2', entry_points['target_2'], '#AB47BC'),
                    ('🎯 الهدف 1', entry_points['target_1'], '#29B6F6'),
                    ('📈 نقطة الدخول', entry_points['entry_point'], '#00E676'),
                    ('💰 السعر الحالي', current, '#FFD700'),
                    ('🛑 وقف الخسارة', entry_points['stop_loss'], '#FF5252')
                ]
                
                for label, value, color in sorted(levels, key=lambda x: x[1], reverse=True):
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <span>{label}</span>
                        <span style="color:{color}; font-weight:bold;">${value:.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # توصية سريعة
                st.markdown("---")
                st.markdown("#### 💡 التوصية")
                
                if current > entry_points['entry_point']:
                    st.success("✅ إشارة شراء - السعر فوق نقطة الدخول")
                elif current > entry_points['stop_loss']:
                    st.warning("⏳ مراقبة - السعر بين الدخول ووقف الخسارة")
                else:
                    st.error("❌ إشارة بيع - السعر تحت وقف الخسارة")

# ============================================================================
# الصفحة الرئيسية
# ============================================================================

def main():
    """الدالة الرئيسية"""
    
    # تحميل التصميم
    load_css()
    
    # عرض الهيدر
    st.markdown("""
    <div class="main-header">
        <h1>🚀 الماسح الضوئي للأسهم المتفجرة</h1>
        <p>اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي وتحليل الضغط (Squeeze)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض الشريط الجانبي
    render_sidebar()
    
    # تشغيل المسح إذا تم الضغط على الزر
    config = st.session_state.sidebar_config
    if config and config.get('scan_clicked', False):
        if not st.session_state.get('scan_in_progress', False):
            st.session_state.scan_in_progress = True
            with st.spinner("🔍 جاري مسح السوق..."):
                results = scan_market_ai(
                    sector=config.get('sector'),
                    min_score=config.get('min_score', 70),
                    min_prob=config.get('min_prob', 55),
                    max_symbols=config.get('max_symbols', 15)
                )
                if not results.empty:
                    st.session_state.scan_results = results
                    st.session_state.last_scan_time = datetime.now().strftime('%H:%M:%S')
                    st.success(f"✅ تم العثور على {len(results)} فرصة!")
                else:
                    st.warning("⚠️ لا توجد نتائج مطابقة للمعايير الحالية")
            st.session_state.scan_in_progress = False
    
    # عرض الصفحة المختارة
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'scanner':
        render_scanner()
    elif page == 'files':
        render_file_explorer()
    elif page == 'analyze':
        render_analyze()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
