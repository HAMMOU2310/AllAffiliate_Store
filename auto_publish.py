import os
import json
from dotenv import load_dotenv
from google import genai

# تفعيل قراءة الملف المخفي فور بدء السكريبت
load_dotenv()

# جلب مفتاح API بأمان من ملف .env
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[!] خطأ: لم يتم العثور على مفتاح API. تأكد من إضافته بشكل صحيح في ملف .env")
    exit(1)

# إعداد عميل Gemini باستخدام المفتاح الآمن
client = genai.Client(api_key=api_key)

# بقية كود السكريبت الخاص بك تستمر من هنا...
JSON_FILE_PATH = "data/products.json"

# ==========================================
# FUNCTIONS
# ==========================================
def scrape_product(url):
    print(f"[*] Analyzing link and scraping product data...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج النص فقط ليقرأه الذكاء الاصطناعي ويصيغ منه الوصف (بدون صور افتراضية)
        text_content = ' '.join([p.text for p in soup.find_all('p')])[:2000]
            
        return {"text": text_content, "url": url}
    except Exception as e:
        print(f"[!] Scraping error: {e}")
        sys.exit(1)

def generate_copy(data, image_url):
    print("[*] Calling Gemini AI to generate high-converting English copy...")
    prompt = f"""
    You are an expert affiliate marketer and professional copywriter. Based on this product text: "{data['text']}"
    Generate a compelling sales copy and return it ONLY as a valid JSON object matching this structure in English:
    {{
        "title": "A catchy, attention-grabbing title under 10 words",
        "description": "A highly persuasive 3-line sales description focusing on the problem, solution, and a clear call-to-action suitable for Pinterest traffic",
        "image_url": "{image_url}",
        "affiliate_link": "{data['url']}",
        "date": "{datetime.now().isoformat()}"
    }}
    Do not add any markdown tags like ```json or any explanations. Return only the raw JSON.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"[!] AI Generation error: {e}")
        sys.exit(1)

def update_database(new_product):
    print("[*] Updating database structure...")
    if os.path.dirname(JSON_FILE_PATH):
        os.makedirs(os.path.dirname(JSON_FILE_PATH), exist_ok=True)
        
    products = []
    
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            try:
                old_data = json.load(f)
                if isinstance(old_data, list):
                    products = old_data
                elif isinstance(old_data, dict) and "products" in old_data:
                    products = old_data["products"]
            except:
                products = []
                
    products.insert(0, new_product)
    
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print(f"[*] New product successfully added to {JSON_FILE_PATH}")

def deploy_to_cloudflare():
    print("[*] Pushing updates to GitHub to trigger Cloudflare build...")
    try:
        subprocess.run(["git", "add", JSON_FILE_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "Add new product with verified true image"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Congratulations! Your International English Store is live on Cloudflare.")
    except Exception as e:
        print(f"[!] Data saved locally, but git push failed: {e}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # التحقق من أنك قمت بإدخال الرابطين معاً في التيرمينال
    if len(sys.argv) < 3:
        print("❌ خطأ: يجب إدخال رابط كليك بانك ورابط الصورة الحقيقية معاً!")
        print('الاستخدام الصحيح: python auto_publish.py "رابط_المنتج" "رابط_الصورة"')
        sys.exit(1)
        
    url = sys.argv[1]
    custom_image_url = sys.argv[2] # الصورة الحقيقية التي أدخلتها أنت
    
    # تمرير البيانات بالترتيب الصحيح
    data = scrape_product(url)
    product_json = generate_copy(data, custom_image_url)
    update_database(product_json)
    deploy_to_cloudflare()