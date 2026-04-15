# MVP 與 Phase 2 建議

## MVP（8~12 週）

- 使用者登入（JWT）
- 角色權限（Admin/Reviewer/Uploader/Viewer）
- 批量上傳（含 hash 去重）
- 指定 invoice type
- AI OCR + 欄位抽取 + 驗證
- 雙閾值自動判斷（clarity/confidence/required fields）
- Manual Review（三欄）
- Save Draft / Approve / Reject / Re-run OCR
- Invoice Search + Detail
- Settings（AI key/model、prompt、invoice type、fields、users/roles）
- 標準化 final JSON 輸出
- 全量 audit log

## Phase 2

- 多 AI provider 智能路由（成本/品質策略）
- 欄位級 confidence UI 熱點顯示
- ERP/Accounting API 整合（SAP/Oracle/NetSuite）
- Excel/CSV 匯出與排程報表
- Dashboard 高階分析（STP, FTR, accuracy trend）
- 批次 approve/assign
- vendor master matching
- duplicate invoice detection（內容語意 + hash hybrid）
- 自動學習：低準確欄位 prompt 優化建議

