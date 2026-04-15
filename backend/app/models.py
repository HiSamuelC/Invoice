import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from .database import Base


class InvoiceStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    OCR_PROCESSING = "OCR_PROCESSING"
    AUTO_APPROVED = "AUTO_APPROVED"
    PENDING_REVIEW = "PENDING_REVIEW"
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(30), nullable=False, default="Viewer")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class InvoiceType(Base):
    __tablename__ = "invoice_types"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    field_definition = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    content_type = Column(String(80), nullable=False)
    storage_path = Column(String(255), nullable=False)
    batch_name = Column(String(120))
    remarks = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    uploaded_file_id = Column(String, ForeignKey("uploaded_files.id"), nullable=False)
    invoice_type_id = Column(String, ForeignKey("invoice_types.id"), nullable=False)
    status = Column(String(30), nullable=False, default=InvoiceStatus.UPLOADED.value)
    assigned_reviewer = Column(String(255))
    clarity_score = Column(Float)
    ai_confidence_score = Column(Float)
    required_fields_complete = Column(Boolean, default=False)
    ocr_text = Column(Text)
    ai_raw_json = Column(JSON)
    final_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    uploaded_file = relationship("UploadedFile")
    invoice_type = relationship("InvoiceType")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String(50), nullable=False)
    actor = Column(String(255))
    before_data = Column(JSON)
    after_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
