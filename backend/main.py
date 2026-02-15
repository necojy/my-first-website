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
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 2. 【關鍵修復】：智慧判斷環境，告訴程式去哪裡找瀏覽器！
    if os.path.exists("./chrome-linux64/chrome"):
        # 👉 情況 A：如果在 Render 雲端，就使用 build.py 下載的攜帶版 Chrome
        chrome_options.binary_location = "./chrome-linux64/chrome"
        service = Service("./chromedriver-linux64/chromedriver")
    else:
        # 👉 情況 B：如果在你的本地端電腦，就維持自動抓取的方法
        service = Service(ChromeDriverManager().install())

    try:
        # 3. 啟動瀏覽器 (這裡的 service 會根據上面判斷的結果來決定)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 4. 命令瀏覽器前往指定網址 (你設定的 YouTube)
        driver.get("https://www.youtube.com/")
        time.sleep(3) 
        page_title = driver.title
        driver.quit()
        
        return {"message": "成功打開瀏覽器並執行完畢！", "網頁標題是": page_title}
        
    except Exception as e:
        return {"message": "啟動瀏覽器失敗", "error": str(e)}