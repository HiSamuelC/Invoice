from typing import Any
from pydantic import BaseModel, Field


class InvoiceTypeCreate(BaseModel):
    code: str
    name: str
    field_definition: dict[str, Any] = Field(default_factory=dict)


class ReviewPayload(BaseModel):
    header_fields: dict[str, Any] = Field(default_factory=dict)
    items: list[dict[str, Any]] = Field(default_factory=list)
    action: str


class OCRResult(BaseModel):
    invoice_type: str
    clarity_score: float
    ai_confidence_score: float
    required_fields_complete: bool
    manual_review_required: bool
    review_reason: list[str]
    header_fields: dict[str, Any]
    items: list[dict[str, Any]]
    full_ocr_text: str
