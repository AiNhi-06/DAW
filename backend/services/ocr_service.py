import re
from pathlib import Path

def normalize_text(text):
    return re.sub(r"\s+", " ", str(text or "").strip())

def parse_common_fields(text):
    text = normalize_text(text)
    output = []
    m = re.search(r"\b\d{12}\b", text)
    if m:
        output.append({"field": "cccd", "value": m.group(0), "confidence": 0.90})
    m = re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b", text)
    if m:
        output.append({"field": "ngay_sinh", "value": m.group(0), "confidence": 0.85})
    if text:
        output.append({"field": "raw_text", "value": text, "confidence": 0.50})
    return output

def run_ocr(path: Path):
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang="vi")
        result = ocr.predict(str(path))
        texts, scores = [], []
        for page in result:
            data = page.json() if hasattr(page, "json") and callable(page.json) else {}
            res = data.get("res", data) if isinstance(data, dict) else {}
            texts.extend(res.get("rec_texts", []) or [])
            scores.extend(res.get("rec_scores", []) or [])
        text = " ".join(texts)
        parsed = parse_common_fields(text)
        if parsed and scores:
            avg = float(sum(scores) / len(scores))
            for item in parsed:
                item["confidence"] = avg
        return parsed
    except Exception:
        return [{"field": "ocr_status", "value": "OCR_CHUA_SAN_SANG", "confidence": 0.0}]
