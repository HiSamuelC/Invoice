# 系統架構圖說明

## 1) 高層架構（Web-based, 前後端分離）

```text
[Browser / Next.js Frontend]
      |
      | HTTPS + JWT
      v
[API Gateway / Backend (FastAPI)]
      |
      |------------------------------|
      |                              |
      v                              v
[PostgreSQL]                 [Object Storage]
(Metadata, Audit,            (Local/S3)
Settings, Users, JSON)
      |
      v
[Job Queue + Worker]
      |
      v
[AI Provider Adapter Layer]
(OpenAI / Azure / Gemini / Claude / Local OCR)
```

## 2) 關鍵設計原則

- **可插拔 AI Provider**：以 `provider interface` 抽象化，隨時更換 API key / model。
- **雙 JSON 保存**：
  - `ai_raw_json`：AI 原始輸出（不可覆寫）
  - `final_json`：最終批核輸出（可版本化）
- **雙閾值 + 完整度判斷**（你補強建議已採納）：
  - `clarity_score >= 90`
  - `ai_confidence_score >= 90`
  - `required_fields_complete = true`
  - 同時成立才可 Auto Approved
- **欄位級 confidence**：每個欄位保留信心分數，供 manual review 高亮。
- **全流程 audit log**：上傳、OCR、修改、批准、拒絕、重跑都留痕。
- **可擴展資料模型**：`invoice_type_fields` 驅動 dynamic form，降低 hardcode。

## 3) 主要資料流

1. 使用者上傳多檔（JPG/JPEG/PNG/PDF）+ 指定 invoice type。
2. 系統計算檔案 hash，檢查重複。
3. 建立 `uploaded_files`、`invoices(status=UPLOADED)`。
4. 丟入 OCR 任務佇列。
5. Worker 執行：
   - OCR 全文提取
   - 欄位抽取
   - 驗證與 review 建議
6. 寫入 `ai_raw_json`、欄位值、items、分數。
7. 自動規則引擎判斷：
   - 達標 => `AUTO_APPROVED`
   - 未達標 => `PENDING_REVIEW`
8. Reviewer 於三欄介面修正後 `SAVE_DRAFT` / `APPROVE` / `REJECT` / `RE_RUN_OCR`。
9. 產生 `final_json`（schema 一致）。

## 4) 非功能需求

- 安全：JWT + RBAC + API key 加密（KMS 或至少 app-level encryption）。
- 可靠：job retry、dead-letter queue、OCR timeout 控制。
- 可觀測：結構化 logs、trace id、錯誤告警。
- 效能：搜尋欄位索引、分頁、批量寫入、非同步 OCR。

