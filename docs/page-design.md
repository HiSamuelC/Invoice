# 頁面設計（UI/UX）

## 1. Login
- Email、Password
- 忘記密碼（可後補）
- 錯誤提示與鎖定策略

## 2. Dashboard
- KPI Cards：今日上傳量、Auto Approved、Pending Review、Rejected
- Trend 圖：日/週處理量
- 待辦清單：指派給我的待批核

## 3. Upload Invoice
- 拖拉區 + 檔案清單
- 必填：invoice type
- 選填：batch name, remarks
- 重複檢查結果提示（hash hit）

## 4. Invoice Search
- 多條件篩選器
- 結果表格（可排序/分頁）
- 行內狀態 badge（色彩分明）

## 5. Manual Review Workspace（三欄）
- 左：待批核清單 + assignment
- 中：viewer（image/pdf）
- 右：dynamic form（依 type fields）
- 操作：Save Draft / Save & Approve / Reject / Re-run OCR

## 6. Invoice Detail
- 基本資訊
- 原始檔案預覽
- OCR 全文
- AI Raw JSON / Final JSON 對照
- 欄位變更歷程 + audit timeline

## 7. Settings
- AI provider、API key、model
- prompt templates（含版本）
- invoice type master
- invoice type fields master
- currency & validation settings

## 8. User & Role Management
- users CRUD
- roles CRUD
- permissions matrix

## 視覺風格
- 企業中性風（灰/藍為主）
- 表格高可讀（行高 44+、固定表頭）
- 狀態色：
  - Approved: Green
  - Pending: Orange
  - Rejected: Red
  - Draft: Blue/Grey

