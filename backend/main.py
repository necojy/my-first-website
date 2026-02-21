from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import undetected_chromedriver as uc

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/open_browser")
def test_browser():
    options = uc.ChromeOptions()
    
    # ⚠️ 【上雲端必備】：推送到 Hugging Face 時，這行不能有 #
    options.add_argument("--headless=new")  
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None

    # 1. 正確初始化瀏覽器
    driver = uc.Chrome(options=options)
    
    # 2. 前往目標網頁 (這裡以 Google 為例，否則截圖會是全白)
    driver.get("https://www.google.com")
    
    # 3. 取得截圖
    screenshot_b64 = driver.get_screenshot_as_base64()

    if driver is not None:
            driver.quit()
    
    # 4. 回傳正確的 JSON (字典) 格式
    return {
        "message": "瀏覽器開啟並截圖成功", 
        "screenshot_base64": screenshot_b64
    }
 
    