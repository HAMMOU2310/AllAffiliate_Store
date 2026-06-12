import sys
import json
import time
import os
from dotenv import load_dotenv
from google import genai

# تفعيل قراءة الملف المخفي .env
load_dotenv()

# جلب المفتاح بأمان
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("[!] خطأ: لم يتم العثور على مفتاح API. تأكد من إضافته في ملف .env")
    sys.exit(1)

# إعداد العميل (الطريقة الجديدة)
client = genai.Client(api_key=GEMINI_API_KEY)

# 2. رابط الصورة الافتراضية
DEFAULT_IMAGE_URL = "https://via.placeholder.com/600x600.png?text=Product+Image+Coming+Soon"

def generate_product_data(product_url, image_url):
    """دالة للتواصل مع جيميناي وتوليد البيانات"""
    prompt = f"""
    Act as an expert copywriter and JSON data formatter.
    Your task is to analyze the product page and generate a JSON object for my store.

    CRITICAL RULES:
    1. Title: You MUST extract and use the FULL, descriptive branding title of the product. DO NOT use short or abbreviated names.
    2. Description: Write a compelling, problem-solving description (3-4 sentences) ending with a strong Call to Action.
    3. Output ONLY the raw JSON object, no markdown formatting.

    Format:
    {{
      "title": "[Full Descriptive Title]",
      "description": "[Compelling Description]",
      "image_url": "{image_url}",
      "affiliate_link": "{product_url}"
    }}

    Inputs:
    Product Link: {product_url}
    Image Link: {image_url}
    """
    
    max_retries = 5 
    retry_delay = 15 

    for attempt in range(max_retries):
        try:
            print(f"جاري معالجة البيانات... (محاولة {attempt + 1}/{max_retries})")
            
            # الاتصال بالنموذج (الطريقة الجديدة)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            output_text = response.text.strip()
            if output_text.startswith("```json"):
                output_text = output_text[7:-3].strip()
            elif output_text.startswith("```"):
                output_text = output_text[3:-3].strip()
                
            return json.loads(output_text)
            
        except Exception as e:
            print(f"حدث خطأ في الاتصال: {e}")
            if attempt < max_retries - 1:
                print(f"جاري الانتظار {retry_delay} ثانية...")
                time.sleep(retry_delay)
            else:
                print("فشلت جميع المحاولات لهذا المنتج.")
                return None

def main():
    args = sys.argv[1:]
    
    if len(args) == 0 or len(args) % 2 != 0:
        print("خطأ: يرجى إدخال الروابط بشكل زوجي. إذا لم توجد صورة، اكتب \"\" أو \"none\".")
        sys.exit(1)

    new_products = []
    
    for i in range(0, len(args), 2):
        prod_url = args[i]
        img_url = args[i+1].strip()
        product_number = (i // 2) + 1
        
        print(f"\n--- البدء في المنتج رقم {product_number} ---")
        
        if img_url == "" or img_url.lower() == "none":
            print("ملاحظة: لم يتم إرفاق صورة. سيتم استخدام الصورة الافتراضية.")
            img_url = DEFAULT_IMAGE_URL
            
        data = generate_product_data(prod_url, img_url)
        
        if data:
            new_products.append(data)
            print(f"تم بنجاح: {data['title']}")
        
        if product_number < (len(args) / 2):
            print("انتظار 10 ثوانٍ لضمان استقرار الاتصال بالـ API...")
            time.sleep(10)

    if not new_products:
        print("\nلم يتم جلب بيانات أي منتج.")
        sys.exit(1)

    # تعديل مسار الملف ليتطابق مع مجلد بيانات متجرك
    file_path = 'data/products.json'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_products = []

    existing_products.extend(new_products)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_products, f, indent=4, ensure_ascii=False)

    print(f"\nتم الانتهاء! تمت إضافة {len(new_products)} منتجات إلى متجرك بنجاح.")

if __name__ == "__main__":
    main()