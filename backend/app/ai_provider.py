from .schemas import OCRResult


class BaseAIProvider:
    def process_invoice(self, file_path: str, invoice_type: str, field_definition: dict) -> OCRResult:
        raise NotImplementedError


class MockAIProvider(BaseAIProvider):
    def process_invoice(self, file_path: str, invoice_type: str, field_definition: dict) -> OCRResult:
        header = {
            key: {"value": None, "confidence": 0} for key in field_definition.get("header_fields", ["invoice_no", "vendor_name", "total_amount", "currency"])
        }
        header["invoice_no"] = {"value": "INV-DEMO-001", "confidence": 96}
        header["vendor_name"] = {"value": "Demo Vendor Ltd.", "confidence": 94}
        header["total_amount"] = {"value": 1234.56, "confidence": 93}
        header["currency"] = {"value": "USD", "confidence": 98}

        clarity = 92
        conf = 93
        required_ok = True
        manual = not (clarity >= 90 and conf >= 90 and required_ok)

        return OCRResult(
            invoice_type=invoice_type,
            clarity_score=clarity,
            ai_confidence_score=conf,
            required_fields_complete=required_ok,
            manual_review_required=manual,
            review_reason=[] if not manual else ["low confidence"],
            header_fields=header,
            items=[{"line_no": 1, "description": "Sample Item", "qty": 1, "unit_price": 1234.56, "amount": 1234.56, "confidence": 90}],
            full_ocr_text="SAMPLE OCR TEXT FROM MOCK PROVIDER"
        )
