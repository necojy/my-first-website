from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定義前端傳過來的資料格式
class InvoiceData(BaseModel):
    invoice_number: str

# 建立一個 POST 路由來接收資料
@app.post("/api/process_invoice")
def process_invoice(data: InvoiceData):
    number = data.invoice_number
    
    # 這裡可以放入你深入的 Python 邏輯（例如爬蟲、演算法運算）
    # 目前我們先做簡單的字串長度與格式檢查示範
    if len(number) == 10:
        result_message = f"成功接收！發票號碼 {number} 格式正確。正在啟動後端查詢程序..."
    else:
        result_message = f"錯誤：發票號碼 {number} 長度不符，請重新輸入。"
        
    return {"message": result_message}