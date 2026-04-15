from datetime import datetime
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import InvoiceType, Invoice, InvoiceStatus, AuditLog
from .schemas import InvoiceTypeCreate, ReviewPayload
from .services import save_upload, run_ocr_and_decide

app = FastAPI(title="AI Invoice Image Processing System", version="1.0.0")
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")
templates = Jinja2Templates(directory="backend/app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    total = db.query(Invoice).count()
    pending = db.query(Invoice).filter(Invoice.status == InvoiceStatus.PENDING_REVIEW.value).count()
    approved = db.query(Invoice).filter(Invoice.status.in_([InvoiceStatus.AUTO_APPROVED.value, InvoiceStatus.APPROVED.value])).count()
    return templates.TemplateResponse("dashboard.html", {"request": request, "total": total, "pending": pending, "approved": approved})


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, db: Session = Depends(get_db)):
    types = db.query(InvoiceType).all()
    return templates.TemplateResponse("upload.html", {"request": request, "types": types})


@app.get("/review", response_class=HTMLResponse)
def review_page(request: Request):
    return templates.TemplateResponse("review.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})


@app.post("/api/invoice-types")
def create_invoice_type(payload: InvoiceTypeCreate, db: Session = Depends(get_db)):
    exists = db.query(InvoiceType).filter(InvoiceType.code == payload.code).first()
    if exists:
        raise HTTPException(status_code=409, detail="invoice type code already exists")
    row = InvoiceType(code=payload.code, name=payload.name, field_definition=payload.field_definition)
    db.add(row)
    db.commit()
    return {"id": row.id, "code": row.code, "name": row.name}


@app.get("/api/invoice-types")
def list_invoice_types(db: Session = Depends(get_db)):
    rows = db.query(InvoiceType).all()
    return [{"id": r.id, "code": r.code, "name": r.name, "field_definition": r.field_definition} for r in rows]


@app.post("/api/uploads/invoices")
async def upload_invoices(invoice_type_id: str = Form(...), batch_name: str | None = Form(None), remarks: str | None = Form(None), files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    invoice_type = db.query(InvoiceType).filter(InvoiceType.id == invoice_type_id).first()
    if not invoice_type:
        raise HTTPException(status_code=404, detail="invoice type not found")

    created = []
    duplicates = []
    for f in files:
        file_bytes = await f.read()
        invoice, err = save_upload(db, file_bytes, f.filename, f.content_type or "application/octet-stream", invoice_type_id, batch_name, remarks)
        if err == "DUPLICATE":
            duplicates.append(f.filename)
            continue
        db.refresh(invoice)
        run_ocr_and_decide(db, invoice)
        created.append(invoice.id)

    db.commit()
    return {"created_invoice_ids": created, "duplicates": duplicates}


@app.get("/api/invoices")
def search_invoices(status: str | None = None, invoice_no: str | None = None, vendor_name: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Invoice)
    if status:
        query = query.filter(Invoice.status == status)
    if invoice_no:
        query = query.filter(Invoice.final_json["header_fields"]["invoice_no"]["value"].as_string() == invoice_no)
    if vendor_name:
        query = query.filter(Invoice.final_json["header_fields"]["vendor_name"]["value"].as_string().ilike(f"%{vendor_name}%"))

    rows = query.order_by(Invoice.created_at.desc()).limit(200).all()
    return [{
        "id": r.id,
        "status": r.status,
        "clarity_score": r.clarity_score,
        "ai_confidence_score": r.ai_confidence_score,
        "final_json": r.final_json,
        "created_at": r.created_at,
    } for r in rows]


@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    r = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="invoice not found")
    logs = db.query(AuditLog).filter(AuditLog.entity_type == "invoice", AuditLog.entity_id == invoice_id).order_by(AuditLog.created_at.desc()).all()
    return {
        "id": r.id,
        "status": r.status,
        "ocr_text": r.ocr_text,
        "ai_raw_json": r.ai_raw_json,
        "final_json": r.final_json,
        "audit_logs": [{"action": l.action, "at": l.created_at, "actor": l.actor} for l in logs]
    }


@app.get("/api/review/queue")
def review_queue(db: Session = Depends(get_db)):
    rows = db.query(Invoice).filter(Invoice.status.in_([InvoiceStatus.PENDING_REVIEW.value, InvoiceStatus.DRAFT.value])).order_by(Invoice.created_at.asc()).all()
    return [{"id": r.id, "status": r.status, "score": r.ai_confidence_score, "clarity": r.clarity_score} for r in rows]


@app.post("/api/review/{invoice_id}")
def review_action(invoice_id: str, payload: ReviewPayload, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")

    before = invoice.final_json
    if payload.action == "SAVE_DRAFT":
        invoice.status = InvoiceStatus.DRAFT.value
    elif payload.action == "APPROVE":
        invoice.status = InvoiceStatus.APPROVED.value
    elif payload.action == "REJECT":
        invoice.status = InvoiceStatus.REJECTED.value
    elif payload.action == "RERUN_OCR":
        invoice.status = InvoiceStatus.OCR_PROCESSING.value
        run_ocr_and_decide(db, invoice)
    else:
        raise HTTPException(status_code=400, detail="invalid action")

    if payload.action in {"SAVE_DRAFT", "APPROVE", "REJECT"}:
        invoice.final_json = {
            **(invoice.final_json or {}),
            "header_fields": payload.header_fields or (invoice.final_json or {}).get("header_fields", {}),
            "items": payload.items or (invoice.final_json or {}).get("items", []),
            "processing_status": invoice.status,
        }

    invoice.updated_at = datetime.utcnow()
    db.add(AuditLog(entity_type="invoice", entity_id=invoice.id, action=payload.action, before_data=before, after_data=invoice.final_json))
    db.commit()
    return {"invoice_id": invoice.id, "status": invoice.status}


@app.get("/health")
def health():
    return {"ok": True}
