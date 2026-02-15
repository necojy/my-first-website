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
    # 1. 設定瀏覽器的啟動選項
    chrome_options = Options()
    
    # 【加入更嚴格的雲端防當機參數】
    chrome_options.add_argument("--headless=new") # 使用新版的無頭模式 (推薦)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu") # 雲端沒有顯示卡，必須禁用
    chrome_options.add_argument("--window-size=1920,1080") # 給定一個虛擬的螢幕解析度
    chrome_options.add_argument("--remote-debugging-port=9222") # 解決 DevToolsActivePort 閃退的關鍵！
    chrome_options.add_argument("--disable-extensions") # 停用擴充功能以節省資源

    # 2. 智慧判斷環境，告訴程式去哪裡找瀏覽器
    if os.path.exists("./chrome-linux64/chrome"):
        # 👉 情況 A：如果在 Render 雲端
        chrome_options.binary_location = "./chrome-linux64/chrome"
        service = Service("./chromedriver-linux64/chromedriver")
    else:
        # 👉 情況 B：如果在你的本地端電腦
        service = Service(ChromeDriverManager().install())

    try:
        # 3. 啟動瀏覽器
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 4. 命令瀏覽器前往指定網址
        driver.get("https://www.youtube.com/")
        time.sleep(3) 
        page_title = driver.title
        driver.quit()
        
        return {"message": "成功打開瀏覽器並執行完畢！", "網頁標題是": page_title}
        
    except Exception as e:
        return {"message": "啟動瀏覽器失敗", "error": str(e)}