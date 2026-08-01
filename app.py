# app.py
"""
التطبيق الرئيسي - نقطة الدخول للماسح الضوئي للأسهم
"""

import streamlit as st
import sys
import os
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="الماسح الضوئي للأسهم",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة المسارات
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# استيراد مكونات الواجهة
from frontend.components.sidebar import render_sidebar
from frontend.components.dashboard import render_dashboard
from frontend.components.file_explorer import render_file_explorer
from frontend.utils.helpers import init_session_state


def main():
    """الدالة الرئيسية للتطبيق"""
    
    # تهيئة حالة الجلسة
    init_session_state()
    
    # عرض الشريط الجانبي
    sidebar_config = render_sidebar()
    
    # المحتوى الرئيسي
    col_main, col_right = st.columns([3, 1])
    
    with col_main:
        # عنوان التطبيق
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;">
            <h1 style="margin:0;">🚀 الماسح الضوئي للأسهم</h1>
            <p style="margin-top:5px; opacity:0.9;">اكتشاف فرص الانفجار السعري باستخدام الذكاء الاصطناعي</p>
            <p style="font-size:0.8rem; opacity:0.7;">⏱️ آخر تحديث: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
        
        # عرض المحتوى حسب الاختيار
        if st.session_state.get('show_file', False):
            render_file_explorer()
        else:
            render_dashboard()
    
    with col_right:
        # معلومات سريعة
        st.markdown("---")
        st.markdown("### 📊 حالة النظام")
        st.metric("الأسهم المتاحة", "150+")
        st.metric("فرص الانفجار", "8", delta="+2")
        st.metric("دقة النموذج", "84.2%", delta="+1.3%")


if __name__ == "__main__":
    main()
