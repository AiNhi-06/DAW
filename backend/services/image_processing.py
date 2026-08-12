import cv2
from pathlib import Path

def inspect_image(path: Path) -> dict:
    img = cv2.imread(str(path))
    if img is None:
        return {"quality": "KHONG_DOC_DUOC", "width": 0, "height": 0}
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    if min(w, h) < 700:
        quality = "THAP"
    elif sharpness < 80:
        quality = "MO"
    elif sharpness < 180:
        quality = "TRUNG_BINH"
    else:
        quality = "TOT"
    return {"quality": quality, "width": w, "height": h, "sharpness": round(float(sharpness), 2)}

def preprocess_image(path: Path) -> Path:
    img = cv2.imread(str(path))
    if img is None:
        return path
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    out = path.with_name(path.stem + "_preprocessed.png")
    cv2.imwrite(str(out), gray)
    return out
