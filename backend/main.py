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

    # 🌟🌟🌟【找回關鍵武器：對抗屈臣氏專用】🌟🌟🌟
    options.add_argument("--disable-http2") # 關閉 HTTP/2，繞過指紋防火牆
    options.add_argument("--ignore-certificate-errors") # 忽略憑證問題
    options.page_load_strategy = 'eager' # 拒絕無限轉圈圈

    driver = None

    # 1. 正確初始化瀏覽器
    driver = uc.Chrome(options=options)
    
    # 🌟 加上超時限制，避免卡死
    driver.set_page_load_timeout(30)
        
    print("開啟 Watsons 訂單頁")
    driver.get("https://www.watsons.com.tw/my-account/orders")  
    # driver.get("https://www.google.com/?hl=zh_TW")
    
    # 3. 取得截圖
    screenshot_b64 = driver.get_screenshot_as_base64()

    if driver is not None:
            driver.quit()
    
    # 4. 回傳正確的 JSON (字典) 格式
    return {
        "message": "瀏覽器開啟並截圖成功", 
        "screenshot_base64": screenshot_b64
    }
 
    