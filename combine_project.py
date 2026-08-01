import os

# المجلدات التي نريد جمع الأكواد منها
TARGET_FOLDERS = ['frontend', 'backend']
# الملفات الفردية المهمة في الجذر
TARGET_FILES = ['app.py', 'config.py']
# الملف الناتج
OUTPUT_FILE = 'full_project_code.txt'

# امتدادات الملفات المراد قراءتها
ALLOWED_EXTENSIONS = ('.py', '.css')

def combine_files():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # 1. طباعة شجرة المشروع
        outfile.write("=" * 80 + "\n")
        outfile.write("PROJECT STRUCTURE & COMBINED CODE\n")
        outfile.write("=" * 80 + "\n\n")

        # 2. قراءة الملفات الفردية
        for file in TARGET_FILES:
            if os.path.exists(file):
                outfile.write(f"\n{'='*30} FILE: {file} {'='*30}\n\n")
                with open(file, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read() + "\n")

        # 3. قراءة المجلدات المحددة
        for folder in TARGET_FOLDERS:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.endswith(ALLOWED_EXTENSIONS):
                            file_path = os.path.join(root, file)
                            outfile.write(f"\n{'='*30} FILE: {file_path} {'='*30}\n\n")
                            try:
                                with open(file_path, 'r', encoding='utf-8') as infile:
                                    outfile.write(infile.read() + "\n")
                            except Exception as e:
                                outfile.write(f"# تعذر قراءة الملف: {e}\n")

    print(f"✅ تم جمع كافة الملفات بنجاح داخل الملف: {OUTPUT_FILE}")

if __name__ == '__main__':
    combine_files()
