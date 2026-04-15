# AI Prompt Engine 設計

## Prompt Types

1. `OCR_FULLTEXT`
2. `FIELD_EXTRACTION`
3. `VALIDATION_REVIEW`

每個 `invoice_type` 可綁定不同 prompt template（含 model/provider）。

---

## 1) OCR 全文提取 Prompt（範例）

```text
You are an OCR engine for invoices.
Extract all visible text exactly as seen from the input document.
Output JSON only:
{
  "ocr_text": "...",
  "language": "...",
  "page_count": 1
}
```

## 2) 發票欄位抽取 Prompt（範例）

```text
You are an invoice extraction engine.
Given invoice type definition and OCR text, extract header fields and line items.
Rules:
- Do not guess unreadable values; return null.
- Keep original format for invoice_no/date/currency.
- Include confidence (0-100) per field.
- Output JSON only.
```

## 3) 驗證與 review 建議 Prompt（範例）

```text
You are a validation assistant.
Check required fields completeness and data quality.
Return:
{
  "clarity_score": 0,
  "ai_confidence_score": 0,
  "required_fields_complete": false,
  "manual_review_required": true,
  "review_reason": ["..."]
}
```

## Prompt Versioning 建議

- 每次修改 template 產生新版本（不可覆寫舊版）
- invoice type 可切換 active prompt version
- 保存每次 OCR 使用的 prompt_version 到 invoice 記錄

