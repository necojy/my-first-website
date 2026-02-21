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
    options.add_argument("--headless=new")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # 🌟 人類偽裝術
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--accept-lang=zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7")

    # 🛡️ 繞過 HTTP/2 阻擋
    options.add_argument("--disable-http2") 
    options.add_argument("--ignore-certificate-errors")
    
    # ⚡ Eager 模式
    options.page_load_strategy = 'eager'

    driver = None

    try:
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        driver.set_page_load_timeout(15)
        
        print("開啟 Watsons 訂單頁...")
        try:
            driver.get("https://www.watsons.com.tw/my-account/orders")
        except TimeoutException:
            driver.execute_script("window.stop();")
        except Exception:
            pass

        time.sleep(3)
 
        # ====================
        # 1. 登入流程 
        # ====================
        try:
            username_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']"))
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
            print("等待登入跳轉中 (12秒)...")
            time.sleep(12)

        except TimeoutException:
            print("未偵測到登入框，可能已登入或被阻擋")

        # ====================
        # 2. 切換門市交易紀錄
        # ====================
        print("切換至門市交易紀錄...")
        try:
            store_records_tab = wait.until(
                EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'nav-item') and contains(.,'門市交易紀錄')]"))
            )
            driver.execute_script("arguments[0].click();", store_records_tab)
            time.sleep(5) 

            # 📸 發生未知嚴重錯誤時，一樣拍照存證！
            screenshot_b64 = driver.get_screenshot_as_base64()
            driver.quit()
            return {"message": "發生預期外的錯誤", "error": str(e), "screenshot_base64": screenshot_b64}
            
        except TimeoutException:
            # # 📸 萬一找不到頁籤，拍下案發現場
            screenshot_b64 = driver.get_screenshot_as_base64()
            # driver.quit()
            # return {"message": "發生錯誤", "error": "找不到門市交易紀錄頁籤", "screenshot_base64": screenshot_b64}

        # ====================
        # 3. 確認並獲取資料
        # ====================
        # print("檢查並載入訂單資料...")
        # items = []
        # try:
        #     wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.orders-containers")))
            
        #     # 等待至少第一筆訂單出現
        #     WebDriverWait(driver, 10).until(
        #         lambda d: len(d.find_elements(By.CSS_SELECTOR, "e2-my-account-order-history-item")) > 0
        #     )
            
        #     items = driver.find_elements(By.CSS_SELECTOR, "e2-my-account-order-history-item")
        #     print(f"✅ 成功抓取 {len(items)} 筆訂單")

            
        
        # except TimeoutException:
        #     driver.quit()
        #     return {"message": "查無訂單紀錄", "資料總筆數": 0, "統計結果": [], "詳細清單": []}


    except Exception as e:
        # if driver:
        #     try:
        #         # 📸 發生未知嚴重錯誤時，一樣拍照存證！
        #         screenshot_b64 = driver.get_screenshot_as_base64()
        #         driver.quit()
        #         return {"message": "發生預期外的錯誤", "error": str(e), "screenshot_base64": screenshot_b64}
        #     except:
        #         pass
        return {"message": "發生最外層預期外的錯誤", "error": str(e)}