import sys
import json
import os
# تأكد من استيراد مكتبة Gemini الخاصة بك هنا كما هي في كودك الحالي
# import google.generativeai as genai 

def add_product_with_custom_image():
    # التأكد من أنك أدخلت الرابطين معاً في التيرمينال
    if len(sys.argv) < 3:
        print("❌ خطأ: يجب إدخال رابط كليك بانك ورابط الصورة معاً!")
        print('الاستخدام الصحيح: python main.py "رابط_المنتج" "رابط_الصورة"')
        return

    product_url = sys.argv[1]
    image_url = sys.argv[2] # الرابط الحقيقي الذي استخرجته أنت بنفسك

    print("⏳ جاري تحليل المنتج وصياغة العنوان والوصف بالذكاء الاصطناعي...")
    
    # -------------------------------------------------------------
    # هنا يوضع كود الذكاء الاصطناعي الخاص بك لجلب العناوين والوصف
    # سأضع هنا نصاً تجريبياً، والسكربت عندك سيعوضه بالذكاء الاصطناعي الخاص بك:
    generated_title = "Unlock Peak Brain Power: Support Memory & Focus Naturally!" 
    generated_description = "Struggling with brain fog? Discover the neuroscience-backed solution to sharpen focus."
    # -------------------------------------------------------------

    # بناء كود المنتج الجديد بالرابط الحقيقي الخاص بك
    new_product = {
        "title": generated_title,
        "description": generated_description,
        "image_url": image_url, # رابط صورتك الحقيقية 100%
        "affiliate_link": product_url,
        "date": "2026-06-10T13:00:00" # تاريخ اليوم تلقائي
    }

    # مسار ملف المنتجات
    file_path = "data/products.json"

    # قراءة المنتجات الحالية وإضافة المنتج الجديد لها
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                products = json.load(file)
            except json.JSONDecodeError:
                products = []
    else:
        products = []

    products.append(new_product)

    # حفظ الملف مجدداً
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

    print("✅ تم بنجاح إنشاء المنتج وصياغته وربطه بصورتك الحقيقية داخل الكود!")

if __name__ == "__main__":
    add_product_with_custom_image()