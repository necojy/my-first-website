from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    options.add_argument("--headless=new")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # 🌟🌟🌟【新增魔法 1：終極人類偽裝術】🌟🌟🌟
    # 騙防火牆這是一台正常的 Windows 電腦，並且使用繁體中文
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--accept-lang=zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7")

    # 🛡️ 魔法 2：繞過 HTTP/2 阻擋
    options.add_argument("--disable-http2") 
    options.add_argument("--ignore-certificate-errors")
    
    # ⚡ 魔法 3：Eager 模式 (不等沒用的廣告，拿到核心網頁就跑)
    options.page_load_strategy = 'eager'

    driver = None

    try:
        driver = uc.Chrome(options=options)
        
        # 設定 15 秒極限
        driver.set_page_load_timeout(15)
        
        print("開啟 Watsons 訂單頁...")
        try:
            driver.get("https://www.watsons.com.tw/my-account/orders")
        except TimeoutException:
            print("⚠️ 載入超時！強制切斷背景渲染！")
            driver.execute_script("window.stop();")
        except Exception as get_err:
            print(f"⚠️ GET 發生其他錯誤: {get_err}")

        # 給網頁 3 秒鐘喘息
        time.sleep(3)
 
        # ====================
        # 1. 登入流程 
        # ====================
        try:
            username_input = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='會員卡號/電子郵件信箱/手機號碼']")
                )
            )
            username_input.clear()
            username_input.send_keys(os.getenv("WATSONS_USERNAME"))
            time.sleep(1)

            password_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='password']"))
            )
            password_input.clear()
            password_input.send_keys(os.getenv("WATSONS_PASSWORD"))
            time.sleep(1)
            
            # password_input.send_keys(Keys.RETURN)
                   
            # 抓取一下當下的網址跟標題
            current_url = driver.current_url
            page_title = driver.title

            # 📸 拍下當下畫面
            screenshot_b64 = driver.get_screenshot_as_base64()

            driver.quit()
        
            
            # 給予登入跳轉時間
            time.sleep(12)

            return {
            "message": "已加上人類偽裝，請查看截圖是否成功抵達屈臣氏！",
            "機器人位置": current_url,
            "網頁標題": page_title,
            "screenshot_base64": screenshot_b64 
            }   

        except TimeoutException:
            print("未偵測到登入框，可能已登入或被阻擋")


    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        return {"message": "發生最外層預期外的錯誤", "error": str(e)}