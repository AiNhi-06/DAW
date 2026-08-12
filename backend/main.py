from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from backend.database import SessionLocal
from backend.models.models import NguoiDung
from backend.services.security import hash_password
from backend.routers import auth, applications

app = FastAPI(
    title="Hệ thống hỗ trợ xét tuyển hồ sơ - Đại học Quy Nhơn",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(applications.router)

@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        user = db.query(NguoiDung).filter(
            NguoiDung.ten_dang_nhap == "admin"
        ).first()
        if not user:
            db.add(NguoiDung(
                ho_ten="Quản trị viên tuyển sinh",
                ten_dang_nhap="admin",
                mat_khau=hash_password("admin123"),
                vai_tro="ADMIN"
            ))
            db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {"system": "QNU Tuyển sinh", "status": "running", "docs": "/docs"}

@app.get("/api/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        q = text("""
            SELECT
              COUNT(*) AS tong,
              COUNT(*) FILTER (WHERE trang_thai='CHO_XU_LY') AS cho_xu_ly,
              COUNT(*) FILTER (WHERE trang_thai='DA_DUYET') AS da_duyet,
              COUNT(*) FILTER (WHERE trang_thai='TU_CHOI') AS tu_choi,
              COUNT(*) FILTER (WHERE trang_thai='CAN_BO_XEM_XET') AS can_xem_xet
            FROM tuyensinh.ho_so
        """)
        return dict(db.execute(q).mappings().one())
    finally:
        db.close()
