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

# ==========================================
# 🛠️ 輔助函式區
# ==========================================
def get_chrome_options():
    """封裝瀏覽器設定，讓主流程保持乾淨"""
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # 偽裝與繞過防火牆設定
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--accept-lang=zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7")
    options.add_argument("--disable-http2") 
    options.add_argument("--ignore-certificate-errors")
    options.page_load_strategy = 'eager'
    return options

def parse_order_html(html_source):
    """專職處理 HTML 解析，分離爬蟲與資料處理邏輯"""
    soup = BeautifulSoup(html_source, 'html.parser')
    items = soup.find_all('e2-my-account-order-history-item')
    
    raw_data = []
    stats = defaultdict(lambda: defaultdict(int))

    for item in items:
        # 優先找桌面版，找不到再找手機版
        data_ul = item.find('ul', class_='desktop-order-data') or item.find('ul', class_='data')
        if not data_ul: continue

        lis = data_ul.find_all('li')
        if len(lis) < 3: continue

        full_date_str = lis[0].text.strip()
        store_name = lis[1].text.strip()
        amount = lis[2].text.strip()

        if not full_date_str: continue

        date_only = full_date_str.split(" ")[0] if " " in full_date_str else full_date_str
        raw_data.append({"日期": full_date_str, "店名": store_name, "金額": amount})
        stats[date_only][store_name] += 1

    # 使用列表推導式 (List Comprehension) 一行完成統計字串
    final_summary = [
        f"{date} 在 {store} 共有 {count} 筆消費" 
        for date in sorted(stats.keys(), reverse=True) 
        for store, count in stats[date].items()
    ]
    
    return raw_data, final_summary

# ==========================================
# 🚀 主 API 路由
# ==========================================
@app.get("/api/open_browser")
def test_browser():
    username = os.getenv("WATSONS_USERNAME")
    password = os.getenv("WATSONS_PASSWORD")
    
    if not username or not password:
        return {"message": "發生錯誤", "error": "找不到帳號或密碼，請檢查 .env 檔案"}

    driver = None

    try:
        # 1. 初始化瀏覽器
        driver = uc.Chrome(options=get_chrome_options())
        wait = WebDriverWait(driver, 20)
        driver.set_page_load_timeout(15)
        
        print("開啟 Watsons 訂單頁...")
        try:
            driver.get("https://www.watsons.com.tw/my-account/orders")
        except TimeoutException:
            driver.execute_script("window.stop();")

        time.sleep(3)
 
        # 2. 登入流程 
        try:
            user_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")))
            user_field.clear()
            user_field.send_keys(username)

            pass_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
            pass_field.clear()
            # 將密碼與 Enter 鍵合併送出，更簡潔
            pass_field.send_keys(password + Keys.RETURN)
            
            print("等待登入跳轉中 (12秒)...")
            time.sleep(12)
        except TimeoutException:
            print("未偵測到登入框，可能已登入或被阻擋")

        # 3. 切換門市交易紀錄
        print("切換至門市交易紀錄...")
        try:
            tab = wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'nav-item') and contains(.,'門市交易紀錄')]")))
            driver.execute_script("arguments[0].click();", tab)
            print("點擊成功，等待資料載入...")
            time.sleep(8) # 合併等待時間
        except TimeoutException:
            return {"message": "發生錯誤", "error": "找不到門市交易紀錄頁籤", "screenshot_base64": driver.get_screenshot_as_base64()}

        # 4. 檢查 HTML 渲染與資料解析
        print("檢查並載入訂單資料...")
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.orders-containers")))
        except TimeoutException:
            return {"message": "查無訂單紀錄", "資料總筆數": 0, "統計結果": [], "詳細清單": []}

        # 將繁雜的 HTML 交給我們寫好的模組處理
        raw_data, final_summary = parse_order_html(driver.page_source)

        return {
            "message": "資料抓取與分析完成！",
            "資料總筆數": len(raw_data),
            "統計結果": final_summary,
            "詳細清單": raw_data
        }

    except Exception as e:
        # 捕捉未知的嚴重錯誤並拍照
        error_response = {"message": "發生最外層預期外的錯誤", "error": str(e)}
        if driver:
            try:
                error_response["screenshot_base64"] = driver.get_screenshot_as_base64()
            except:
                pass
        return error_response
        
    finally:
        # 🌟 終極防漏水：不管上面是 return 還是噴 Error，最後都一定會執行這裡把瀏覽器關掉！
        if driver:
            try:
                driver.quit()
            except:
                pass