# 1. 使用官方的 Python 基礎系統
FROM python:3.10-slim

# 2. 安裝系統必備的底層元件與 Google Chrome
RUN apt-get update && apt-get install -y wget unzip curl gnupg \
    && curl -fSsL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /usr/share/keyrings/google-chrome.gpg > /dev/null \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. 🌟【HF 專屬規定】：建立非 root 使用者 (ID: 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 4. 設定工作資料夾
WORKDIR $HOME/app

# 5. 複製並安裝 Python 套件 (給予 user 權限)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 複製你的所有後端程式碼到系統內
COPY --chown=user . .

# 7. 🌟【HF 專屬規定】：啟動 FastAPI 伺服器的大腦，大門必須開在 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]