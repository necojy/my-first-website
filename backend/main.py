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
    
    valid_accounts = [acc for acc in accounts if acc["user"] and acc["pass"]]

    if not valid_accounts:
        return {"message": "發生錯誤", "error": "找不到任何帳號或密碼，請檢查 .env 檔案"}

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--accept-lang=zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7")
    options.add_argument("--disable-http2") 
    options.add_argument("--ignore-certificate-errors")
    options.page_load_strategy = 'eager'

    driver = None
    all_raw_data = []  # 🌟 用來存放所有帳號的總資料
    stats = defaultdict(lambda: defaultdict(int))
    error_screenshot = ""

    try:
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        driver.set_page_load_timeout(20)

        # 🌟 開始迴圈：依序處理每一個帳號
        for acc in valid_accounts:
            print(f"啟動機器人，準備處理: {acc['label']}")
            try:
                # 🌟 關鍵：切換帳號前，先連上首頁並清空 Cookie (強制登出)
                driver.get("https://www.watsons.com.tw")
                driver.delete_all_cookies()
                time.sleep(1)

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
                username_input = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']"))
                )
                username_input.clear()
                username_input.send_keys(acc["user"]) # 使用迴圈當前的帳號
                time.sleep(1)

                password_input = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='password']"))
                )
                password_input.clear()
                password_input.send_keys(acc["pass"]) # 使用迴圈當前的密碼
                time.sleep(1)
                
                password_input.send_keys(Keys.RETURN)
                time.sleep(12) # 等待登入跳轉

                # ====================
                # 2. 切換門市交易紀錄
                # ====================
                store_records_tab = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'nav-item') and contains(.,'門市交易紀錄')]"))
                )
                driver.execute_script("arguments[0].click();", store_records_tab)
                time.sleep(5) 

                # ====================
                # 3. 獲取與解析資料
                # ====================
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.orders-containers")))
                time.sleep(3) 

                page_html = driver.page_source
                soup = BeautifulSoup(page_html, 'html.parser')
                items = soup.find_all('e2-my-account-order-history-item')

                for item in items:
                    data_ul = item.find('ul', class_='desktop-order-data')
                    if not data_ul:
                        data_ul = item.find('ul', class_='data')

                    if data_ul:
                        lis = data_ul.find_all('li')
                        if len(lis) >= 5:
                            full_date_str = lis[0].text.strip()
                            store_name = lis[1].text.strip()
                            amount = lis[2].text.strip()
                            points_earned = lis[3].text.strip()
                            points_used = lis[4].text.strip()

                            if not full_date_str: continue

                            date_only = full_date_str.split(" ")[0] if " " in full_date_str else full_date_str

                            products = []
                            detail_blocks = item.find_all('div', class_='order-details')
                            
                            for block in detail_blocks:
                                name_elem = block.find('div', class_='product-name')
                                qty_elem = block.find('div', class_='product-quantity')
                                
                                if name_elem and qty_elem:
                                    p_name = name_elem.text.replace('\n', '').strip()
                                    p_name = ' '.join(p_name.split()) 
                                    p_qty = qty_elem.text.strip()
                                    products.append({"商品名稱": p_name, "數量": p_qty})

                            # 🌟 將抓到的單筆資料加入總清單，並標記是哪個帳號的
                            all_raw_data.append({
                                "歸屬帳號": acc["label"],
                                "日期": date_only,
                                "店名": store_name,
                                "金額": amount,
                                "獲得點數": points_earned,
                                "使用點數": points_used,
                                "購買商品清單": products
                            })
                            stats[date_only][store_name] += 1

            except Exception as e:
                print(f"{acc['label']} 發生錯誤跳過: {e}")
                error_screenshot = driver.get_screenshot_as_base64() # 記下最後一次錯誤的畫面
                continue # 🌟 就算這個帳號失敗，也會繼續執行下一個帳號！

        # 迴圈結束，整理統計
        final_summary = []
        sorted_dates = sorted(stats.keys(), reverse=True)
        for date in sorted_dates:
            for store, count in stats[date].items():
                final_summary.append(f"{date} 在 {store} 共有 {count} 筆消費")

        driver.quit()

        if len(all_raw_data) == 0 and error_screenshot:
            return {"message": "所有帳號皆抓取失敗", "screenshot_base64": error_screenshot}

        return {
            "message": f"成功抓取 {len(valid_accounts)} 組帳號的資料！",
            "資料總筆數": len(all_raw_data),
            "統計結果": final_summary,
            "詳細清單": all_raw_data
        }

    except Exception as e:
        if driver:
            try:
                screenshot_b64 = driver.get_screenshot_as_base64()
                driver.quit()
                return {"message": "發生最外層預期外的錯誤", "error": str(e), "screenshot_base64": screenshot_b64}
            except:
                pass
        return {"message": "發生最外層預期外的錯誤", "error": str(e)}