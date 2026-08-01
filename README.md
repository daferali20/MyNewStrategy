# MyNewStrategy
MyNewStrategy/
│
├── .gitignore               # تجاهل الملفات المؤقتة والبيئة الافتراضية
├── requirements.txt         # المكتبات المطلوبة للمشروع
├── README.md                # وصف المشروع وطريقة التشغيل
├── app.py                   # الصفحة الرئيسية للتطبيق (Streamlit Main)
│
├── pages/                   # الواجهات الفرعية في Streamlit
│   └── 1_📊_Dashboard.py
│
└── backend/                 # محرك الحسابات والبيانات (معزول عن الواجهة)
    ├── __init__.py          # (ملف فارغ لتعريف الموديول)
    ├── data_loader.py       # جلب البيانات
    └── analytics.py         # التحليلات والمؤشرات
