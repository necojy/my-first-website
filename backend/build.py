import os
import urllib.request
import zipfile

print("Step 1: 安裝 requirements.txt...")
os.system("pip install -r requirements.txt")

print("Step 2: 準備下載 Chrome 瀏覽器 (Linux 版)...")
# 如果沒有下載過，才去下載
if not os.path.exists("./chrome-linux64"):
    print("下載 Chrome 中...")
    urllib.request.urlretrieve("https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/linux64/chrome-linux64.zip", "chrome.zip")
    with zipfile.ZipFile("chrome.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    os.remove("chrome.zip")

if not os.path.exists("./chromedriver-linux64"):
    print("下載 ChromeDriver 中...")
    urllib.request.urlretrieve("https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/linux64/chromedriver-linux64.zip", "driver.zip")
    with zipfile.ZipFile("driver.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    os.remove("driver.zip")

print("Step 3: 設定執行權限 (讓雲端電腦可以開啟它)...")
os.system("chmod +x ./chrome-linux64/chrome")
os.system("chmod +x ./chromedriver-linux64/chromedriver")

print("建置完美結束！")