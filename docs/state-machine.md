# 狀態流轉設計

## Invoice Processing Status

- `UPLOADED`
- `OCR_PROCESSING`
- `OCR_DONE`
- `AUTO_APPROVED`
- `PENDING_REVIEW`
- `DRAFT`
- `APPROVED`
- `REJECTED`
- `ERROR`

## Assignment Status

- `UNASSIGNED`
- `ASSIGNED`
- `REVIEWED`

## 狀態轉移（簡化）

```text
UPLOADED -> OCR_PROCESSING -> OCR_DONE
OCR_DONE -> AUTO_APPROVED (if rule pass)
OCR_DONE -> PENDING_REVIEW (if rule fail)
PENDING_REVIEW -> DRAFT (save draft)
DRAFT -> APPROVED (save & approve)
PENDING_REVIEW -> APPROVED (direct approve)
PENDING_REVIEW/DRAFT -> REJECTED
PENDING_REVIEW/DRAFT -> OCR_PROCESSING (re-run OCR)
any -> ERROR (exception)
```

## Auto Approve 規則

僅當以下條件全部成立：

1. `clarity_score >= 90`
2. `ai_confidence_score >= 90`
3. `required_fields_complete = true`

否則進入 `PENDING_REVIEW`。

