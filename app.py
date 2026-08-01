import sys
import os
import streamlit as st

# إضافة مسار المشروع لتفادي أخطاء الاستيراد عند النشر
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.data_loader import DataLoader

st.set_page_config(
    page_title="مشروعي الجديد",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ منصة التحليل والاستكشاف الجديدة")
st.write("مرحباً بك! المشروع جاهز ومبني على هيكلية نظيفة وقابلة لللتوسع.")

ticker = st.text_input("أدخل رمز السهم (مثل NVDA, AAPL):", value="NVDA")

if st.button("تحميل البيانات"):
    with st.spinner("جاري جلب البيانات..."):
        df = DataLoader.get_stock_data(ticker)
        if not df.empty:
            st.success(f"تم جلب {len(df)} شمعة بنجاح!")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.error("لم يتم العثور على بيانات لهذه الشركة.")
