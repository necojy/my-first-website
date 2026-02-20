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
    options.add_argument("--headless=new")  # 上線再開
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
        # 登入流程
        # ====================
        try:
            username_input = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")
                )
            )
            print("偵測到登入框，執行登入...")
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

            wait.until(EC.url_contains("orders"))
            time.sleep(3)

        except TimeoutException:
            print("未偵測到登入框，可能已登入或頁面載入過慢")

        # ====================
        # 切換門市交易紀錄
        # ====================
        print("切換至門市交易紀錄...")
        try:
            store_records_tab = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//li[contains(@class,'nav-item') and contains(.,'門市交易紀錄')]")
                )
            )
            driver.execute_script("arguments[0].click();", store_records_tab)
            time.sleep(3) 

        except TimeoutException:
            return {"message": "發生錯誤", "error": "找不到門市交易紀錄頁籤"}

        # ====================
        # 確認並獲取資料 (無須滾動)
        # ====================
        print("檢查並載入訂單資料...")
        items = []
        try:
            # 確保容器存在
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.orders-containers")))
            
            # 檢查是否有第一筆項目 (等待其渲染)
            WebDriverWait(driver, 5).until(
                lambda d: len(
                    d.find_elements(By.CSS_SELECTOR, "e2-my-account-order-history-item")
                ) > 0
            )
            
            # 直接抓取所有現存的項目
            items = driver.find_elements(By.CSS_SELECTOR, "e2-my-account-order-history-item")
            print(f"✅ 成功抓取 {len(items)} 筆訂單")

        except TimeoutException:
            print("查無訂單")
            driver.quit()
            return {"message": "查無訂單紀錄", "資料總筆數": 0, "統計結果": [], "詳細清單": []}

        # ====================
        # 解析資料
        # ====================
        raw_data = []
        stats = defaultdict(lambda: defaultdict(int))

        for item in items:
            try:
                # 優先使用桌面版 selector，若抓不到才試手機版
                try:
                    data_ul = item.find_element(By.CSS_SELECTOR, "ul.desktop-order-data")
                except:
                    data_ul = item.find_element(By.CSS_SELECTOR, "ul.data")

                lis = data_ul.find_elements(By.TAG_NAME, "li")

                if len(lis) < 3:
                    continue

                full_date_str = lis[0].text.strip()
                store_name = lis[1].text.strip()
                amount = lis[2].text.strip()

                if not full_date_str: 
                    continue

                date_only = full_date_str.split(" ")[0] if " " in full_date_str else full_date_str

                raw_data.append({
                    "日期": full_date_str,
                    "店名": store_name,
                    "金額": amount
                })

                stats[date_only][store_name] += 1

            except Exception:
                continue

        # ====================
        # 統計整理
        # ====================
        final_summary = []
        sorted_dates = sorted(stats.keys(), reverse=True)

        for date in sorted_dates:
            for store, count in stats[date].items():
                final_summary.append(f"{date} 在 {store} 共有 {count} 筆消費")

        driver.quit()

        return {
            "message": "資料抓取完成",
            "資料總筆數": len(raw_data),
            "統計結果": final_summary,
            "詳細清單": raw_data,
        }

    except Exception as e:
        # 確保發生預期外錯誤時，驅動程式能正確關閉
        if driver:
            try:
                driver.quit()
            except:
                pass

        return {"message": "發生錯誤", "error": str(e)}