from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立一個新的爬蟲測試 API
@app.get("/api/scrape_test")
def scrape_website():
    # 1. 目標網址 (這裡以一個簡單的範例網站為例)
    target_url = "https://example.com/"
    
    try:
        # 2. 發送請求去抓取網頁
        response = requests.get(target_url, verify=False)
        response.encoding = 'utf-8' # 確保中文不會變成亂碼
        
        # 3. 使用 BeautifulSoup 解析網頁原始碼
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 4. 抓取網頁中的 <h1> 標籤文字
        title = soup.find("h1").text
        
        return {"message": "爬蟲成功！", "scraped_title": title}
        
    except Exception as e:
        return {"message": "爬蟲失敗", "error": str(e)}