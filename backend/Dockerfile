# 1. 使用官方的 Python 基礎系統
FROM python:3.10-slim

# 2. 設定工作資料夾
WORKDIR /app

# 3. 安裝系統必備的底層元件與真正的 Google Chrome 瀏覽器
RUN apt-get update && apt-get install -y wget unzip curl gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. 複製你的 requirements.txt 並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 複製你的所有後端程式碼到系統內
COPY . .

# 6. 啟動 FastAPI 伺服器的大腦
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]