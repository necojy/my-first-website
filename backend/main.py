from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允許任何前端網頁來連線 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 極簡測試 API
@app.get("/api/test_connection")
def test_connection():
    return {
        "status": "success",
        "message": "🎉 太棒了！Vercel 成功連線到 Hugging Face 後端了！",
        "details": "基礎連線通道暢通無阻。"
    }