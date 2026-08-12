from pathlib import Path
from uuid import uuid4
from datetime import datetime
import hashlib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.config import UPLOAD_DIR
from backend.database import get_db
from backend.models.models import ThiSinh, HoSo, LoaiGiayTo, GiayTo, OCRResult, CanhBao
from backend.services.image_processing import inspect_image, preprocess_image
from backend.services.ocr_service import run_ocr
from backend.services.rule_engine import validate_application

router = APIRouter(prefix="/api/ho-so", tags=["Hồ sơ"])

@router.post("/nop")
async def nop_ho_so(
    ho_ten: str = Form(...),
    ngay_sinh: str = Form(""),
    gioi_tinh: str = Form(""),
    cccd: str = Form(""),
    email: str = Form(""),
    so_dien_thoai: str = Form(""),
    ma_loai: list[int] = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    if len(files) != len(ma_loai):
        raise HTTPException(400, "Số loại giấy tờ không khớp số file.")

    thi_sinh = db.query(ThiSinh).filter(ThiSinh.cccd == cccd).first() if cccd else None
    if not thi_sinh:
        thi_sinh = ThiSinh(
            ho_ten=ho_ten,
            ngay_sinh=datetime.strptime(ngay_sinh, "%Y-%m-%d").date() if ngay_sinh else None,
            gioi_tinh=gioi_tinh or None,
            cccd=cccd or None,
            email=email or None,
            so_dien_thoai=so_dien_thoai or None
        )
        db.add(thi_sinh)
        db.flush()

    token = hashlib.sha256(f"{thi_sinh.ma_thi_sinh}-{uuid4()}".encode()).hexdigest()
    hs = HoSo(
        ma_thi_sinh=thi_sinh.ma_thi_sinh,
        ngay_nop=datetime.utcnow(),
        trang_thai="DANG_XU_LY",
        qr_hash=token
    )
    db.add(hs)
    db.flush()

    ocr_items = []
    warnings = []

    for upload, type_id in zip(files, ma_loai):
        safe_name = Path(upload.filename).name
        ext = Path(safe_name).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".pdf"}:
            raise HTTPException(400, f"Không hỗ trợ định dạng {ext}")

        folder = UPLOAD_DIR / str(hs.ma_ho_so)
        folder.mkdir(parents=True, exist_ok=True)
        destination = folder / f"{uuid4().hex}_{safe_name}"
        destination.write_bytes(await upload.read())

        quality = "KHONG_AP_DUNG"
        processed = destination
        if ext != ".pdf":
            info = inspect_image(destination)
            quality = info["quality"]
            processed = preprocess_image(destination)
            if quality in {"THAP", "MO"}:
                warnings.append(("CHAT_LUONG_ANH", f"Ảnh {safe_name} có chất lượng {quality}.", "TRUNG_BINH"))

        loai = db.query(LoaiGiayTo).filter(LoaiGiayTo.ma_loai == type_id).first()
        if not loai:
            raise HTTPException(400, f"Không tồn tại loại giấy tờ {type_id}")

        gt = GiayTo(
            ma_ho_so=hs.ma_ho_so,
            ma_loai=type_id,
            ten_file=safe_name,
            duong_dan=str(destination.relative_to(UPLOAD_DIR)),
            chat_luong_anh=quality
        )
        db.add(gt)
        db.flush()

        if ext != ".pdf":
            results = run_ocr(processed)
            for item in results:
                db.add(OCRResult(
                    ma_giay_to=gt.ma_giay_to,
                    truong_du_lieu=item["field"],
                    gia_tri=item["value"],
                    do_tin_cay=item["confidence"]
                ))
                ocr_items.append({**item, "file": safe_name})

    types = []
    for gt in db.query(GiayTo).filter(GiayTo.ma_ho_so == hs.ma_ho_so).all():
        loai = db.query(LoaiGiayTo).filter(LoaiGiayTo.ma_loai == gt.ma_loai).first()
        types.append(loai.ten_loai)

    warnings.extend(validate_application(cccd, types, ocr_items))

    for typ, desc, level in warnings:
        db.add(CanhBao(
            ma_ho_so=hs.ma_ho_so,
            loai_loi=typ,
            mo_ta=desc,
            muc_do=level
        ))

    hs.trang_thai = "CAN_BO_XEM_XET" if warnings else "CHO_XU_LY"
    db.commit()

    return {
        "success": True,
        "ma_ho_so": hs.ma_ho_so,
        "qr_hash": token,
        "trang_thai": hs.trang_thai,
        "so_canh_bao": len(warnings),
        "canh_bao": [
            {"type": a, "description": b, "level": c} for a, b, c in warnings
        ]
    }

@router.get("")
def list_applications(db: Session = Depends(get_db)):
    rows = db.query(HoSo, ThiSinh).join(
        ThiSinh, HoSo.ma_thi_sinh == ThiSinh.ma_thi_sinh
    ).order_by(HoSo.ma_ho_so.desc()).all()

    return [{
        "ma_ho_so": hs.ma_ho_so,
        "ho_ten": ts.ho_ten,
        "cccd": ts.cccd,
        "email": ts.email,
        "ngay_nop": hs.ngay_nop.isoformat(),
        "trang_thai": hs.trang_thai
    } for hs, ts in rows]

@router.get("/{ma_ho_so}")
def get_application(ma_ho_so: int, db: Session = Depends(get_db)):
    hs = db.query(HoSo).filter(HoSo.ma_ho_so == ma_ho_so).first()
    if not hs:
        raise HTTPException(404, "Không tìm thấy hồ sơ")
    ts = db.query(ThiSinh).filter(ThiSinh.ma_thi_sinh == hs.ma_thi_sinh).first()

    documents = []
    for gt in db.query(GiayTo).filter(GiayTo.ma_ho_so == hs.ma_ho_so).all():
        loai = db.query(LoaiGiayTo).filter(LoaiGiayTo.ma_loai == gt.ma_loai).first()
        ocr = db.query(OCRResult).filter(OCRResult.ma_giay_to == gt.ma_giay_to).all()
        documents.append({
            "ma_giay_to": gt.ma_giay_to,
            "loai": loai.ten_loai,
            "ten_file": gt.ten_file,
            "chat_luong_anh": gt.chat_luong_anh,
            "ocr": [
                {"truong": x.truong_du_lieu, "gia_tri": x.gia_tri, "do_tin_cay": x.do_tin_cay}
                for x in ocr
            ]
        })

    warnings = db.query(CanhBao).filter(CanhBao.ma_ho_so == hs.ma_ho_so).all()

    return {
        "ma_ho_so": hs.ma_ho_so,
        "trang_thai": hs.trang_thai,
        "qr_hash": hs.qr_hash,
        "thi_sinh": {
            "ma_thi_sinh": ts.ma_thi_sinh,
            "ho_ten": ts.ho_ten,
            "ngay_sinh": ts.ngay_sinh.isoformat() if ts.ngay_sinh else None,
            "gioi_tinh": ts.gioi_tinh,
            "cccd": ts.cccd,
            "email": ts.email,
            "so_dien_thoai": ts.so_dien_thoai
        },
        "giay_to": documents,
        "canh_bao": [{
            "ma_canh_bao": x.ma_canh_bao,
            "loai_loi": x.loai_loi,
            "mo_ta": x.mo_ta,
            "muc_do": x.muc_do,
            "ngay_tao": x.ngay_tao.isoformat()
        } for x in warnings]
    }

@router.patch("/{ma_ho_so}/trang-thai")
def update_status(ma_ho_so: int, status: str, db: Session = Depends(get_db)):
    allowed = {"CHO_XU_LY", "DANG_XU_LY", "CAN_BO_XEM_XET", "DA_DUYET", "TU_CHOI"}
    if status not in allowed:
        raise HTTPException(400, "Trạng thái không hợp lệ")
    hs = db.query(HoSo).filter(HoSo.ma_ho_so == ma_ho_so).first()
    if not hs:
        raise HTTPException(404, "Không tìm thấy hồ sơ")
    hs.trang_thai = status
    db.commit()
    return {"success": True, "trang_thai": status}
