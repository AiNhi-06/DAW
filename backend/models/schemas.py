from datetime import date
from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    ten_dang_nhap: str
    mat_khau: str

class ThiSinhCreate(BaseModel):
    ho_ten: str
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[str] = None
    cccd: Optional[str] = None
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
