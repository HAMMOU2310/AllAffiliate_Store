import sys
import json
import subprocess
import requests
from bs4 import BeautifulSoup
from google import genai
import os
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
# Put your Gemini API Key here
api_key = "YOUR_API_KEY_HERE"

client = genai.Client(api_key=GEMINI_API_KEY)
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
        
        text_content = ' '.join([p.text for p in soup.find_all('p')])[:2000]
        
        image_url = "https://images.unsplash.com/photo-1490645935967-10de6ba17061?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
        og_image = soup.find('meta', property='og:image')
        if og_image:
            image_url = og_image['content']
            
        return {"text": text_content, "image_url": image_url, "url": url}
    except Exception as e:
        print(f"[!] Scraping error: {e}")
        sys.exit(1)

def generate_copy(data):
    print("[*] Calling Gemini AI to generate high-converting English copy...")
    prompt = f"""
    You are an expert affiliate marketer and professional copywriter. Based on this product text: "{data['text']}"
    Generate a compelling sales copy and return it ONLY as a valid JSON object matching this structure in English:
    {{
        "title": "A catchy, attention-grabbing title under 10 words",
        "description": "A highly persuasive 3-line sales description focusing on the problem, solution, and a clear call-to-action suitable for Pinterest traffic",
        "image_url": "{data['image_url']}",
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
        subprocess.run(["git", "commit", "-m", "Switch store to English and add new product"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Congratulations! Your International English Store is live on Cloudflare.")
    except Exception as e:
        print(f"[!] Data saved locally, but git push failed: {e}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_publish.py <product_url>")
        sys.exit(1)
        
    url = sys.argv[1]
    data = scrape_product(url)
    product_json = generate_copy(data)
    update_database(product_json)
    deploy_to_cloudflare()