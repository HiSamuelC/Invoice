# 前端頁面結構（Next.js App Router）

```text
app/
  (auth)/
    login/page.tsx
  (main)/
    dashboard/page.tsx
    invoices/
      upload/page.tsx
      search/page.tsx
      [invoiceId]/page.tsx
      manual-review/page.tsx
    settings/
      ai/page.tsx
      prompts/page.tsx
      invoice-types/page.tsx
      invoice-type-fields/page.tsx
      users/page.tsx
      roles/page.tsx
```

## 主要元件拆分

- `components/upload/DropzoneUploader.tsx`
- `components/invoice/InvoiceTable.tsx`
- `components/review/ReviewQueuePanel.tsx`（左欄）
- `components/review/InvoiceViewerPanel.tsx`（中欄）
- `components/review/DynamicFieldFormPanel.tsx`（右欄）
- `components/common/StatusBadge.tsx`
- `components/common/AuditTimeline.tsx`

## Manual Review Workspace 互動設計

### 左欄（待批核清單）
- 狀態顯示：`PENDING_REVIEW`, `DRAFT`, `ASSIGNED`
- 排序：upload time / low confidence first
- 快速指派 reviewer

### 中欄（發票預覽）
- 圖像縮放、旋轉
- PDF 分頁
- OCR overlay（可選）

### 右欄（動態表單）
- 按 invoice type fields 自動生成
- 低 confidence 欄位高亮
- 顯示 AI 值 vs 人工值
- 操作按鈕：Save Draft / Save & Approve / Reject / Re-run OCR

