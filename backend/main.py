from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv
from collections import defaultdict
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

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

    if not os.getenv("WATSONS_USERNAME") or not os.getenv("WATSONS_PASSWORD"):
        return {"message": "發生錯誤", "error": "找不到帳號或密碼，請檢查 .env 檔案"}

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")  # 雲端保持開啟
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None

    try:
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)

        print("開啟 Watsons 訂單頁")
        driver.get("https://www.watsons.com.tw/my-account/orders")

        # ====================
        # 1. 登入流程
        # ====================
        try:
            username_input = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")
                )
            )
            username_input.clear()
            username_input.send_keys(os.getenv("WATSONS_USERNAME"))
            time.sleep(1)

            password_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='password']"))
            )
            password_input.clear()
            password_input.send_keys(os.getenv("WATSONS_PASSWORD"))
            time.sleep(1)
            
            # 送出登入
            password_input.send_keys(Keys.RETURN)
            
            # 🌟 修正點：拿掉強制 driver.get()，改為單純耐心等待 12 秒，讓網頁自己處理跳轉與載入
            time.sleep(12)

        except TimeoutException:
            print("未偵測到登入框，可能已登入")

        # ====================
        # 2. 切換門市交易紀錄
        # ====================
        print("切換至門市交易紀錄...")
        try:
            store_records_tab = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//li[contains(@class,'nav-item') and contains(.,'門市交易紀錄')]")
                )
            )
            driver.execute_script("arguments[0].click();", store_records_tab)
            time.sleep(5) 

        except TimeoutException:
            current_url = driver.current_url
            page_title = driver.title
            # 📸 🌟 終極武器：如果找不到按鈕，直接拍一張照片 (Base64格式) 回傳給前端！
            screenshot_b64 = driver.get_screenshot_as_base64()
            driver.quit()
            return {
                "message": "發生錯誤", 
                "error": "找不到門市交易紀錄頁籤",
                "機器人當下位置 (URL)": current_url,
                "機器人當下看到的標題": page_title,
                "screenshot": screenshot_b64
            }

        # 🌟 階段二測試成功回傳
        driver.quit()
        return {
            "status": "success",
            "message": "階段二測試通過：成功切換到「門市交易紀錄」！",
            "統計結果": ["頁籤切換成功！"]
        }

    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        return {"message": "發生預期外的錯誤", "error": str(e)}