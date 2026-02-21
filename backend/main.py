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
    
    # ⚠️ 【上雲端必備】：推送到 Hugging Face 時，這行不能有 #
    options.add_argument("--headless=new")  
    
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
        # 1. 登入流程 (已測試通過 ✅)
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
            password_input.send_keys(Keys.RETURN)
            screenshot_b64 = driver.get_screenshot_as_base64()

            wait.until(EC.url_contains("orders"))
            time.sleep(3)
            
            screenshot_b64 = driver.get_screenshot_as_base64()
            return {"message": "發生錯誤", "error": "找不到門市交易紀錄頁籤，請確認 XPath 是否正確或畫面是否載入完全","screenshot": screenshot_b64}

        except TimeoutException:
            print("未偵測到登入框，可能已登入")

        # ====================
        # 2. 切換門市交易紀錄 (🌟 本次測試重點)
        # ====================
        print("切換至門市交易紀錄...")
        try:
            screenshot_b64 = driver.get_screenshot_as_base64()
            # driver.quit()
            
        
            # # 確保元素存在於 HTML 中
            # store_records_tab = wait.until(
            #     EC.presence_of_element_located(
            #         (By.XPATH, "//li[contains(@class,'nav-item') and contains(.,'門市交易紀錄')]")
            #     )
            # )
            # # 使用 JS 強制點擊
            # driver.execute_script("arguments[0].click();", store_records_tab)
            
            # # 給網頁 5 秒鐘去呼叫後端 API 載入表格資料
            # time.sleep(5) 

        except TimeoutException:
            driver.quit()
            return {"message": "發生錯誤", "error": "找不到門市交易紀錄頁籤，請確認 XPath 是否正確或畫面是否載入完全","screenshot": screenshot_b64}

        # 🌟 階段二測試點：成功點擊並等待資料載入後，直接回傳
        driver.quit()
        return {
            "status": "success",
            "message": "階段二測試通過：成功切換到「門市交易紀錄」！",
            "統計結果": [
                "如果看到這行，代表 JavaScript 強制點擊大法在雲端也生效了！",
                "準備進入最終階段：抓取並解析 HTML 資料！"
            ]
        }

        # ====================
        # 3. 確認並獲取資料 (維持註解)
        # ====================
        # ... 

        # ====================
        # 4. 解析資料與統計 (維持註解)
        # ====================
        # ...

    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        return {"message": "發生預期外的錯誤", "error": str(e)}