# Web-based AI Invoice Image Processing System (FastAPI)

## Run

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## What is implemented

- Web pages: Dashboard, Upload, Search, Manual Review (3-column), Settings
- Batch upload endpoint with duplicate detection by SHA-256
- AI OCR provider plugin interface + mock provider
- Auto-approve decision rule:
  - clarity_score >= 90
  - ai_confidence_score >= 90
  - required_fields_complete = true
- Unified final JSON output and AI raw JSON retention
- Manual review actions: Save Draft / Approve / Reject / Re-run OCR
- Basic audit logs

## Notes

- Default DB URL is sqlite for quick start. Set `DATABASE_URL` to PostgreSQL in production.
- For real OCR, replace `MockAIProvider` with your AI vendor implementation.
