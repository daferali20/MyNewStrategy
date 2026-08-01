# run_scanner.py
"""
تشغيل الماسح الذكي للأسهم
"""

from backend.scanner.ai_breakout_analyzer import BreakoutScannerAI
import pandas as pd

def main():
    print("🚀 الماسح الذكي للانفجارات السعرية")
    print("=" * 50)
    
    # إنشاء الماسح
    scanner = BreakoutScannerAI()
    
    # خيارات المسح
    print("\n📊 خيارات المسح:")
    print("1. مسح السوق بالكامل")
    print("2. مسح قطاع معين")
    print("3. تحليل سهم محدد")
    print("4. الخروج")
    
    while True:
        choice = input("\nاختر الخيار (1-4): ")
        
        if choice == '1':
            print("\n🔍 جاري مسح السوق بالكامل...")
            results = scanner.scan_market(min_squeeze=60, min_probability=55)
            
            if not results.empty:
                print(f"\n🔥 تم العثور على {len(results)} فرصة:")
                print(results.to_string(index=False))
                
                # حفظ النتائج
                results.to_csv(f'breakout_opportunities_{pd.Timestamp.now().strftime("%Y%m%d")}.csv', index=False)
                print(f"\n✅ تم حفظ النتائج في ملف CSV")
            else:
                print("❌ لا توجد فرص حالياً")
                
        elif choice == '2':
            sectors = ['التكنولوجيا', 'المالية', 'الرعاية الصحية', 'الاستهلاك', 'الطاقة']
            print("\nالقطاعات المتاحة:")
            for i, sector in enumerate(sectors, 1):
                print(f"{i}. {sector}")
            
            sector_choice = input("\nاختر رقم القطاع: ")
            try:
                sector = sectors[int(sector_choice) - 1]
                print(f"\n🔍 جاري مسح قطاع {sector}...")
                results = scanner.scan_market(sector=sector, min_squeeze=60, min_probability=55)
                
                if not results.empty:
                    print(f"\n🔥 تم العثور على {len(results)} فرصة في قطاع {sector}:")
                    print(results.to_string(index=False))
                else:
                    print(f"❌ لا توجد فرص في قطاع {sector}")
            except:
                print("❌ اختيار غير صحيح")
                
        elif choice == '3':
            symbol = input("أدخل رمز السهم (مثال: AAPL): ").upper()
            print(f"\n📈 تحليل السهم {symbol}...")
            analysis = scanner.analyze_symbol(symbol)
            
            if 'error' in analysis:
                print(f"❌ {analysis['error']}")
            else:
                print(f"\n📊 نتائج تحليل {symbol}:")
                print(f"الشركة: {analysis.get('company_name', symbol)}")
                print(f"القطاع: {analysis.get('sector', 'غير معروف')}")
                print(f"درجة الضغط: {analysis.get('squeeze_score', 0)}/100")
                print(f"احتمالية الانفجار: {analysis.get('breakout_probability', 0)}%")
                print(f"العائد المتوقع: {analysis.get('expected_upside', 0)}%")
                print(f"مستوى المخاطرة: {analysis.get('risk_level', 'غير معروف')}")
                print(f"توقيت الانفجار: {analysis.get('time_to_breakout', 'غير معروف')}")
                
                entry = analysis.get('entry_points', {})
                if entry:
                    print(f"\n🎯 مستويات الدخول والخروج:")
                    print(f"السعر الحالي: ${entry.get('current_price', 0):.2f}")
                    print(f"نقطة الدخول: ${entry.get('entry_point', 0):.2f}")
                    print(f"وقف الخسارة: ${entry.get('stop_loss', 0):.2f}")
                    print(f"الهدف 1: ${entry.get('target_1', 0):.2f}")
                    print(f"الهدف 2: ${entry.get('target_2', 0):.2f}")
        
        elif choice == '4':
            print("👋 مع السلامة!")
            break
        else:
            print("❌ خيار غير صحيح")

if __name__ == "__main__":
    main()
