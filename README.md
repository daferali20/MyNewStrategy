# MyNewStrategy
# 🚀 الماسح الضوئي للأسهم المتفجرة

تطبيق متكامل لمسح الأسهم الأمريكية واكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي.

## 📋 الميزات

- 📊 مسح آلي للأسهم الأمريكية
- 🤖 تحليل بالذكاء الاصطناعي
- 📈 رسوم بيانية تفاعلية
- 📂 مستكشف الملفات المدمج
- ⚙️ إعدادات مرنة

## 🚀 التشغيل

```bash
MyNewStrategy-main/
├── app.py                         # المدخل الرئيسي لنظام Streamlit وتوجيه الصفحات
├── config.py                      # إعدادات النظام، المفاتيح، والمسارات الافتراضية
├── requirements.txt               # الاعتمادات المكتبية
├── backend/                       # المحرك الأساسي (Core Engine)
│   ├── data_loader.py             # جلب بيانات الأسهم (YFinance / AlphaVantage)
│   ├── scanner/                   # وحدات المسح التكتيكي واكتشاف الفرص
│   │   ├── ai_breakout_analyzer.py # المحلل الرئيسي مع دمج الذكاء الاصطناعي
│   │   ├── breakout_scanner.py    # فاحص الاختراقات الفنية
│   │   ├── intraday_scanner.py    # فاحص المضاربة اللحظية
│   │   └── screener.py            # فلترة الأسهم المتقدمة
│   └── explosive_moves/           # موديولات الحركات السعرية المتفجرة (9 ملفات)
│       ├── squeeze_detector.py    # انضغاط Bollinger Bands & Keltner Channels
│       ├── volatility.py          # قياس وانكماش التقلبات (ATR / Historical Vol)
│       ├── compression.py         # انضغاط مدى الشموع (Range Compression)
│       ├── volume_expansion.py    # انفجار وتحليل الأحجام (Volume Spike)
│       ├── smart_money.py         # تتبع السيولة الذكية (OBV / VWAP Flow)
│       ├── breakout_probability.py# احتمالية نجاح الاختراق
│       ├── options_flow.py        # تدفق العقود والخيارات (اختياري)
│       ├── ai_predictor.py        # نموذج التنبؤ الذكي
│       ├── score.py               # تجميع وتصنيف الدرجة النهائية
│       └── integration.py         # المدمج الشامل لموديل explosive_moves
└── frontend/                      # طبقة العرض والواجهات (UI Components)
    ├── assets/style.css           # تنسيقات الواجهة وتأثيرات CSS
    ├── components/                # المكونات المساعدة (Sidebar, Cards, Charts)
    ├── pages/                     # الصفحات المستقلة (Dashboard, Scanner, Analyze)
    └── utils/                     # مساعدة الجلسات (helpers.py, state.py)
