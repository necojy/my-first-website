# --- 請把最上面原本匯入 webdriver 的部分改成這樣 ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv

# 🌟【全新武器】：匯入隱身版 Chrome
import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# 🌟【補回你不小心刪除的大腦核心設定】：
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
    # 1. 使用隱身版的 Options
    options = uc.ChromeOptions()
    
    # 【本地測試】：先不要用 headless，親眼看它登入
    # options.add_argument("--headless=new") 
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu") # 🌟 補上這個：Linux 雲端環境保險參數

    # 🌟 新增這兩個：徹底關閉圖形渲染與進階沙盒限制，防止雲端記憶體不足或當機
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-software-rasterizer")

    options.add_argument("--window-size=1920,1080")

    try:
        # 🌟【關鍵改變】：明確指定 Docker 內的 Chrome 路徑，防止 uc 在雲端迷路！
        driver = uc.Chrome(
            options=options, 
            headless=True,
            browser_executable_path="/usr/bin/google-chrome" # 👈 直接綁定我們在 Dockerfile 裡裝好的 Chrome
        ) 

        # 3. 前往屈臣氏登入頁面
        driver.get("https://www.watsons.com.tw/login")
        wait = WebDriverWait(driver, 15)
        
        # 4. 輸入帳號
        username_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")))
        username_input.clear()
        username_input.send_keys(os.getenv("WATSONS_USERNAME")) # 從保險箱拿帳號
        time.sleep(1.5)

        # 5. 輸入密碼並使用 Enter 送出
        password_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
        password_input.clear()
        password_input.send_keys(os.getenv("WATSONS_PASSWORD")) # 從保險箱拿密碼
        time.sleep(1.5)
        
        password_input.send_keys(Keys.RETURN)

        # 點擊後暫停 8 秒等待跳轉
        time.sleep(8) 
        
        current_url = driver.current_url
        page_title = driver.title
        driver.quit()
        
        return {
            "message": "隱身登入測試完成！", 
            "登入後的網址": current_url,
            "網頁標題是": page_title
        }
        
    except Exception as e:
        # 確保發生錯誤時也能關閉瀏覽器
        if 'driver' in locals():
            driver.quit()
        return {"message": "自動登入發生錯誤", "error": str(e)}