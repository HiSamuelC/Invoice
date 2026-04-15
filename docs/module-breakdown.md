# 功能模組清單（可供開發使用）

## Backend（FastAPI 建議）

1. **Auth & Identity Module**
   - login/logout/refresh
   - users/roles/permissions
   - RBAC middleware

2. **Invoice Type Config Module**
   - invoice_types CRUD
   - invoice_type_fields CRUD
   - required/validation rule 設定

3. **Upload Module**
   - 批量上傳
   - hash 去重
   - file metadata + storage path

4. **OCR Orchestration Module**
   - 建立工作任務
   - provider adapter call
   - 統一 AI response 正規化

5. **Rule Engine Module**
   - auto-approve 判斷
   - 必填欄位完整度檢查
   - 進階商業驗證（金額、日期、幣別）

6. **Manual Review Module**
   - 待審清單
   - assignment（unassigned / assigned / reviewed）
   - save draft / approve / reject / rerun
   - value diff/版本記錄

7. **Search & Query Module**
   - 多條件查詢
   - 詳細頁（原圖、OCR text、JSON、audit）

8. **Prompt Engine Module**
   - prompt templates CRUD
   - invoice type 綁定 prompt
   - provider/model 版本管理

9. **Settings Module**
   - API key、model、currency allowed list
   - system-level feature flags

10. **Audit Module**
    - 審計紀錄查詢
    - 行為追蹤

## Frontend（Next.js 建議）

1. Auth pages + session guard
2. Dashboard（數據卡 + 待辦）
3. Upload（drag-drop + metadata）
4. Invoice Search（篩選 + 表格）
5. Manual Review Workspace（三欄）
6. Invoice Detail（OCR / JSON / history）
7. Settings（AI, prompt, type, fields）
8. User & Role Management

