from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv
from collections import defaultdict
from bs4 import BeautifulSoup 
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
@app.get("/api/open_browser")
def test_browser():
    # 🌟 動態建立帳號清單 (支援無限擴充，完全不用改 code！)
    accounts = []
    
    # 1. 先抓取預設的第一組 (沒有數字後綴的)
    if os.getenv("WATSONS_USERNAME") and os.getenv("WATSONS_PASSWORD"):
        accounts.append({
            "user": os.getenv("WATSONS_USERNAME"), 
            "pass": os.getenv("WATSONS_PASSWORD"), 
            "label": "帳號 1"
        })

    # 2. 自動偵測第 2 組 ~ 第 20 組 (假設你最多加到 20 個)
    for i in range(2, 21):
        user_val = os.getenv(f"WATSONS_USERNAME_{i}")
        pass_val = os.getenv(f"WATSONS_PASSWORD_{i}")
        
        # 只要有找到對應的環境變數，就自動加進排程裡！
        if user_val and pass_val:
            accounts.append({
                "user": user_val, 
                "pass": pass_val, 
                "label": f"帳號 {i}"
            })

    # 檢查是否至少有一組帳號
    if not accounts:
        return {"message": "發生錯誤", "error": "找不到任何帳號或密碼，請檢查環境變數設定"}

    # 後面的 options = uc.ChromeOptions() 都不用動...