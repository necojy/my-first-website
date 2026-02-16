from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 引入 Selenium 相關套件
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os  # 新增這行：用來偵測環境

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/open_browser")
def test_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        # Docker 已經幫我們把系統環境裝好了，直接用最乾淨的寫法！
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://www.google.com/?hl=zh_TW")
        time.sleep(3) 
        page_title = driver.title
        driver.quit()
        
        return {"message": "成功打開瀏覽器並執行完畢！", "網頁標題是": page_title}
        
    except Exception as e:
        return {"message": "啟動瀏覽器失敗", "error": str(e)}