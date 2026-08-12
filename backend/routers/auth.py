from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import NguoiDung
from backend.models.schemas import LoginRequest
from backend.services.security import verify_password

router = APIRouter(prefix="/api/auth", tags=["Đăng nhập"])

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(
        NguoiDung.ten_dang_nhap == data.ten_dang_nhap
    ).first()
    if not user or not verify_password(data.mat_khau, user.mat_khau):
        raise HTTPException(401, "Sai tên đăng nhập hoặc mật khẩu")
    return {
        "success": True,
        "ma_nguoi_dung": user.ma_nguoi_dung,
        "ho_ten": user.ho_ten,
        "vai_tro": user.vai_tro
    }
