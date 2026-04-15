import hashlib
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from .ai_provider import MockAIProvider
from .models import UploadedFile, Invoice, InvoiceStatus, AuditLog

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ai_provider = MockAIProvider()


def save_upload(db: Session, file_bytes: bytes, filename: str, content_type: str, invoice_type_id: str, batch_name: str | None, remarks: str | None):
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    duplicated = db.query(UploadedFile).filter(UploadedFile.file_hash == file_hash).first()
    if duplicated:
        return None, "DUPLICATE"

    safe_name = f"{datetime.utcnow().timestamp()}_{filename}"
    full_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(full_path, "wb") as f:
        f.write(file_bytes)

    uploaded = UploadedFile(
        file_name=filename,
        file_hash=file_hash,
        content_type=content_type,
        storage_path=full_path,
        batch_name=batch_name,
        remarks=remarks,
    )
    db.add(uploaded)
    db.flush()

    invoice = Invoice(uploaded_file_id=uploaded.id, invoice_type_id=invoice_type_id, status=InvoiceStatus.OCR_PROCESSING.value)
    db.add(invoice)
    db.flush()

    return invoice, None


def run_ocr_and_decide(db: Session, invoice: Invoice):
    field_def = invoice.invoice_type.field_definition if invoice.invoice_type else {}
    result = ai_provider.process_invoice(invoice.uploaded_file.storage_path, invoice.invoice_type.code if invoice.invoice_type else "unknown", field_def)

    auto_ok = result.clarity_score >= 90 and result.ai_confidence_score >= 90 and result.required_fields_complete
    invoice.status = InvoiceStatus.AUTO_APPROVED.value if auto_ok else InvoiceStatus.PENDING_REVIEW.value
    invoice.clarity_score = result.clarity_score
    invoice.ai_confidence_score = result.ai_confidence_score
    invoice.required_fields_complete = result.required_fields_complete
    invoice.ocr_text = result.full_ocr_text
    invoice.ai_raw_json = result.model_dump()

    final_payload = {
        "system_invoice_id": invoice.id,
        "source_file_name": invoice.uploaded_file.file_name,
        "invoice_type": result.invoice_type,
        "processing_status": invoice.status,
        "clarity_score": result.clarity_score,
        "ai_confidence_score": result.ai_confidence_score,
        "source_info": {
            "batch_name": invoice.uploaded_file.batch_name,
            "file_hash": invoice.uploaded_file.file_hash,
            "storage_uri": invoice.uploaded_file.storage_path,
        },
        "header_fields": result.header_fields,
        "items": result.items,
        "full_ocr_text": result.full_ocr_text,
        "validation_result": {
            "required_fields_complete": result.required_fields_complete,
            "errors": result.review_reason,
        },
    }
    invoice.final_json = final_payload
    invoice.updated_at = datetime.utcnow()

    db.add(AuditLog(entity_type="invoice", entity_id=invoice.id, action="OCR_COMPLETED", after_data=json.loads(json.dumps(final_payload))))
