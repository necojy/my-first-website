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

    screenshot_b64 = driver.get_screenshot_as_base64()
    return {"message": "發生錯誤", "error": "找不到門市交易紀錄頁籤，請確認 XPath 是否正確或畫面是否載入完全","screenshot": screenshot_b64}



    # try:
    #     driver = uc.Chrome(options=options)
    #     wait = WebDriverWait(driver, 20)

    #     print("開啟 Watsons 訂單頁")
    #     driver.get("https://www.watsons.com.tw/my-account/orders")

        
    #     screenshot_b64 = driver.get_screenshot_as_base64()
    #     return {"message": "發生錯誤", "error": "找不到門市交易紀錄頁籤，請確認 XPath 是否正確或畫面是否載入完全","screenshot": screenshot_b64}

    # except Exception as e:
    #     if driver:
    #         try:
    #             driver.quit()
    #         except:
    #             pass
    #     return {"message": "發生預期外的錯誤", "error": str(e)}