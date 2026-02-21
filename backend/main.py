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
    
    # 魔法指令：繞過 HTTP/2 阻擋
    options.add_argument("--disable-http2") 
    options.add_argument("--ignore-certificate-errors")

    driver = None

    try:
        driver = uc.Chrome(options=options)
        
        # 🌟 【戰術核心】：只給 15 秒！時間一到立刻拋出超時警告，不讓伺服器 500 崩潰
        driver.set_page_load_timeout(15)
        
        print("開啟 Watsons 訂單頁...")
        try:
            # 這裡就是剛剛發生崩潰的地方，我們用 try 包起來保護伺服器
            driver.get("https://www.watsons.com.tw/my-account/orders")
        except TimeoutException:
            # 🌟 時間到！強制切斷背景的惡意迴圈驗證！
            print("⚠️ 載入超時！強制切斷背景渲染！")
            driver.execute_script("window.stop();")
        except Exception as get_err:
            print(f"⚠️ GET 發生其他錯誤: {get_err}")

        # 給網頁 3 秒鐘喘息，看能不能把殘餘的畫面畫出來
        time.sleep(3)
        
        # 抓取一下當下的網址跟標題
        current_url = driver.current_url
        page_title = driver.title

        # 📸 終極武器：拍下當下畫面，看屈臣氏到底在畫面塞了什麼！
        screenshot_b64 = driver.get_screenshot_as_base64()

        driver.quit()
        
        # 💡 故意不回傳 "統計結果"，這樣前端網頁就會跑到 else 區塊，把這張截圖印出來！
        return {
            "message": "已成功強行切斷載入，請查看下方截圖！",
            "機器人位置": current_url,
            "網頁標題": page_title,
            "screenshot": screenshot_b64
        }

    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        return {"message": "發生最外層預期外的錯誤", "error": str(e)}