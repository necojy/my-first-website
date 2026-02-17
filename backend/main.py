# --- 檔案最上方的 import 區塊請改成這樣 ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv

# 🌟【換回標準 Selenium 與輕量隱身套件】
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth # 輕量級隱形迷彩
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/open_browser")
def test_browser():
    options = Options()
    
    # 【本地測試時請把這行加上 # 註解，要上雲端前再打開】
    options.add_argument("--headless=new") 
    
    # 雲端保命與省記憶體參數 (保留)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--blink-settings=imagesEnabled=false") # 不載入圖片省記憶體
    options.add_argument("--window-size=1280,720")

    try:
        # 1. 啟動標準版 Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 2. 🌟【套上輕量級隱形迷彩】：用 JavaScript 偽裝成真人的電腦
        stealth(driver,
            languages=["zh-TW", "zh-CN", "zh"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
        # 3. 前往屈臣氏登入頁面
        driver.get("https://www.watsons.com.tw/login")
        wait = WebDriverWait(driver, 15)
        
        # 4. 輸入帳號
        username_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")))
        username_input.clear()
        username_input.send_keys(os.getenv("WATSONS_USERNAME"))
        time.sleep(1.5)

        # 5. 輸入密碼並使用 Enter 送出
        password_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
        password_input.clear()
        password_input.send_keys(os.getenv("WATSONS_PASSWORD"))
        time.sleep(1.5)
        
        password_input.send_keys(Keys.RETURN)

        # 點擊後暫停 8 秒等待跳轉
        time.sleep(8) 
        
        current_url = driver.current_url
        page_title = driver.title
        driver.quit()
        
        return {
            "message": "輕量隱身登入測試完成！", 
            "登入後的網址": current_url,
            "網頁標題是": page_title
        }
        
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return {"message": "自動登入發生錯誤", "error": str(e)}