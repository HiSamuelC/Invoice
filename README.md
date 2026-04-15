# AI Invoice Image Processing System

此 Repo 現在包含「可執行的 Web-based MVP」與先前的完整設計文件：

- `backend/`：FastAPI Web 系統（Dashboard / Upload / Search / Manual Review / Settings）
- `db/schema.sql`：完整 PostgreSQL schema（生產建議）
- `docs/`：架構、API、狀態流與 UX 規劃

## 快速啟動（MVP Web）

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

開啟：`http://127.0.0.1:8000`

## 已實作重點

- 批量上傳檔案（含 SHA-256 去重）
- 上傳需指定 invoice type
- AI OCR provider 可插拔介面（預設 mock provider）
- 自動判斷規則：clarity/confidence/required fields 三條件
- 未達標進入 Pending Review
- Manual Review 三欄式頁面（左清單／中預覽／右動態欄位區）
- Save Draft / Approve / Reject / Re-run OCR API
- 保存 AI Raw JSON + Final JSON
- Audit Log 基礎記錄

