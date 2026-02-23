from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
import tempfile
import shutil
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
def test_browser():
    accounts = []
    
    u1 = os.getenv("WATSONS_USERNAME")
    p1 = os.getenv("WATSONS_PASSWORD")
    l1 = os.getenv("WATSONS_LABEL", "帳號 1") 
    
    if u1 and p1:
        accounts.append({"user": u1, "pass": p1, "label": l1})

    # for i in range(2, 21):
    #     u = os.getenv(f"WATSONS_USERNAME_{i}")
    #     p = os.getenv(f"WATSONS_PASSWORD_{i}")
    #     l = os.getenv(f"WATSONS_LABEL_{i}", f"帳號 {i}") 
    #     if u and p:
    #         accounts.append({"user": u, "pass": p, "label": l})

    # if not accounts:
    #     return {"message": "發生錯誤", "error": "找不到任何帳號或密碼，請檢查環境變數設定"}

    all_raw_data = []  
    all_coupons_data = [] 
    stats = defaultdict(lambda: defaultdict(int))
    error_screenshot = ""

    for acc in accounts:
        driver = None
        temp_dir = tempfile.mkdtemp()
        
        try:
            print(f"🚀 啟動【完全隔離】瀏覽器，準備處理: {acc['label']}")
            
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
            options.add_argument(f"--user-data-dir={temp_dir}")
            
            driver = uc.Chrome(options=options)
            wait = WebDriverWait(driver, 20)
            driver.set_page_load_timeout(20)

            # ==========================================
            # 1. 登入流程
            # ==========================================
            try:
                driver.get("https://www.watsons.com.tw/my-account/orders")
            except TimeoutException:
                driver.execute_script("window.stop();")
            except Exception:
                pass
            time.sleep(2)
    
            username_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")))
            username_input.clear()
            username_input.send_keys(acc["user"]) 
            time.sleep(1)

            password_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
            password_input.clear()
            password_input.send_keys(acc["pass"]) 
            time.sleep(1)
            
            password_input.send_keys(Keys.RETURN)
            time.sleep(12) 

            # ==========================================
            # 🌟 2. 先抓取優惠券 (這時候點擊最穩！)
            # ==========================================
            print(f"🎟️ {acc['label']} 先抓取優惠卷...")
            try:
                coupon_tab = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my-account/ecouponsEvouchers')]"))
                )
                driver.execute_script("arguments[0].click();", coupon_tab)
                print(f"👉 成功跳轉優惠卷，等待載入...")
                time.sleep(6) 
                
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "e2-my-account-current-coupon")))
                    time.sleep(2) 
                except:
                    pass

                coupon_html = driver.page_source
                soup_coupon = BeautifulSoup(coupon_html, 'html.parser')
                coupon_items = soup_coupon.find_all('div', class_='coupon-item')
                
                for c in coupon_items:
                    name_elem = c.find('div', class_='name')
                    date_elem = c.find('div', class_='date')
                    expiring_elem = c.find('span', class_='expiring')
                    
                    if name_elem and date_elem:
                        c_name = name_elem.text.replace('\n', '').strip()
                        c_date = date_elem.text.replace('\n', '').strip()
                        c_status = "⚠️ 即將到期" if expiring_elem else "✅ 正常"
                        
                        all_coupons_data.append({
                            "歸屬帳號": acc["label"],
                            "名稱": c_name,
                            "到期日": c_date,
                            "狀態": c_status
                        })
                print(f"✅ 抓到 {len(coupon_items)} 張優惠卷！")
            except Exception as e:
                print(f"⚠️ 優惠卷抓取失敗: {e}")

            # ==========================================
            # 🌟 3. 再抓取門市訂單
            # ==========================================
            print(f"📦 {acc['label']} 接著切換回訂單頁面...")
            try:
                # 先點擊左側選單回到「訂單查詢」
                orders_menu = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my-account/orders')]"))
                )
                driver.execute_script("arguments[0].click();", orders_menu)
                time.sleep(4)

                # 切換到門市交易紀錄
                store_records_tab = wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'nav-item') and contains(.,'門市交易紀錄')]")))
                driver.execute_script("arguments[0].click();", store_records_tab)
                time.sleep(3) 

                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.orders-containers")))
                time.sleep(2) 

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
                print(f"✅ 訂單抓取完畢！")
            except Exception as e:
                print(f"⚠️ 訂單抓取失敗: {e}")

        except Exception as e:
            print(f"❌ {acc['label']} 發生錯誤跳過: {type(e).__name__} - {e}")
            if driver:
                try:
                    error_screenshot = driver.get_screenshot_as_base64()
                except:
                    pass
            continue 
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            print(f"💤 {acc['label']} 處理完畢，機器人休息 8 秒鐘...")
            time.sleep(8)

    final_summary = []
    sorted_dates = sorted(stats.keys(), reverse=True)
    for date in sorted_dates:
        for store, count in stats[date].items():
            final_summary.append(f"{date} 在 {store} 共有 {count} 筆消費")

    if len(all_raw_data) == 0 and len(all_coupons_data) == 0 and error_screenshot:
        return {"message": "所有帳號皆抓取失敗", "screenshot_base64": error_screenshot}

    return {
        "message": f"成功抓取 {len(accounts)} 組帳號的資料！",
        "資料總筆數": len(all_raw_data),
        "統計結果": final_summary,
        "詳細清單": all_raw_data,
        "優惠卷清單": all_coupons_data
    }