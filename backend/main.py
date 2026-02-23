from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
import tempfile
import shutil
from dotenv import load_dotenv
import undetected_chromedriver as uc
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
    # 🌟 簡單測試模式：只抓第一組帳號來測
    u1 = os.getenv("WATSONS_USERNAME")
    p1 = os.getenv("WATSONS_PASSWORD")
    
    if not u1 or not p1:
        return {"message": "發生錯誤", "error": "找不到帳號密碼"}

    driver = None
    temp_dir = tempfile.mkdtemp()
    
    try:
        print("🚀 啟動【簡單測試模式】瀏覽器...")
        
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")  
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        options.add_argument("--lang=zh-TW")
        options.add_argument(f"--user-data-dir={temp_dir}")
        options.page_load_strategy = 'eager'
        
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        driver.set_page_load_timeout(20)

        # ==========================================
        # 1. 先登入 (一定要先登入才能看優惠券！)
        # ==========================================
        print("1. 前往登入頁面...")
        driver.get("https://www.watsons.com.tw/my-account/orders")
        time.sleep(3)

        print("2. 輸入帳密...")
        username_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")))
        username_input.clear()
        username_input.send_keys(u1) 
        time.sleep(1)

        password_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
        password_input.clear()
        password_input.send_keys(p1) 
        time.sleep(1)
        
        password_input.send_keys(Keys.RETURN)
        print("3. 等待登入跳轉 (12秒)...")
        time.sleep(12) 

        # ==========================================
        # 2. 測試點擊並跳轉優惠券
        # ==========================================
        print("4. 準備點擊「折價券/提貨券」...")
        try:
            coupon_tab = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my-account/ecouponsEvouchers')]"))
            )
            driver.execute_script("arguments[0].click();", coupon_tab)
            print("👉 成功點擊選單！等待 8 秒讓 Angular 畫圖...")
            time.sleep(8)
            
        except Exception as e:
            print(f"⚠️ 點擊失敗，發生錯誤：{e}")

        # ==========================================
        # 3. 拍照並回傳給前端
        # ==========================================
        print("📸 拍照存證！")
        c_screenshot = driver.get_screenshot_as_base64()
        
        # 🌟 刻意把照片放在 screenshot_base64 欄位，這樣你的前端就會自動把它當作圖片印出來！
        return {
            "message": "測試完成！請查看下方的機器人視角截圖",
            "screenshot_base64": c_screenshot,
            "統計結果": [], # 給空陣列避免前端報錯
            "詳細清單": []  # 給空陣列避免前端報錯
        }

    except Exception as e:
        err_img = ""
        if driver:
            try: err_img = driver.get_screenshot_as_base64()
            except: pass
        return {"message": f"發生錯誤: {e}", "screenshot_base64": err_img}
        
    finally:
        if driver:
            try: driver.quit()
            except: pass
        try: shutil.rmtree(temp_dir, ignore_errors=True)
        except: pass