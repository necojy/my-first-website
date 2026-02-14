from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 引入 Selenium 相關套件
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

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
    
    # 【關鍵設定】：如果要部署到 Render，必須把下面這行取消註解（讓它變成無頭模式）
    chrome_options.add_argument("--headless") 
    
    # 為了避免在某些環境下報錯，加入以下安全參數
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        # 2. 自動下載驅動程式並啟動 Google Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 3. 命令瀏覽器前往指定網址 (我們去一個有名的測試網站)
        driver.get("https://www.youtube.com/")
        
        # 為了讓你能在本地端看清楚它真的有打開，我們讓程式刻意暫停 3 秒鐘
        time.sleep(3) 
        
        # 4. 抓取網頁的標題文字
        page_title = driver.title
        
        # 5. 任務完成，關閉瀏覽器 (這步非常重要，不然你的電腦會累積一堆沒關的視窗)
        driver.quit()
        
        return {"message": "成功打開瀏覽器並執行完畢！", "網頁標題是": page_title}
        
    except Exception as e:
        return {"message": "啟動瀏覽器失敗", "error": str(e)}