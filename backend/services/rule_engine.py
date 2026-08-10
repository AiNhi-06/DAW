from pathlib import Path
import json

RULES = Path(__file__).resolve().parents[2] / "rules" / "tuyensinh.json"

def validate_application(cccd, document_types, ocr_items):
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    warnings = []
    present = set(document_types)
    for required in rules["required_documents"]:
        if required not in present:
            warnings.append(("THIEU_GIAY_TO", f"Thiếu giấy tờ: {required}", "CAO"))

    for item in ocr_items:
        confidence = item.get("confidence", 0)
        if confidence < rules["ocr_confidence_warning"]:
            warnings.append((
                "OCR_DO_TIN_CAY_THAP",
                f"OCR của {item.get('file')} có độ tin cậy thấp.",
                "TRUNG_BINH"
            ))
        if item.get("field") == "cccd" and cccd and item.get("value") != cccd:
            warnings.append((
                "SAI_CCCD",
                "CCCD trên giấy tờ khác CCCD thí sinh kê khai.",
                "NGHIEM_TRONG"
            ))
    return warnings
