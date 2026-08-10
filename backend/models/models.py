from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class ThiSinh(Base):
    __tablename__ = "thi_sinh"
    __table_args__ = {"schema": "tuyensinh"}
    ma_thi_sinh = Column(Integer, primary_key=True)
    ho_ten = Column(String(100), nullable=False)
    ngay_sinh = Column(Date)
    gioi_tinh = Column(String(10))
    cccd = Column(String(12), unique=True)
    email = Column(String(100))
    so_dien_thoai = Column(String(15))
    ho_so = relationship("HoSo", back_populates="thi_sinh")

class NguoiDung(Base):
    __tablename__ = "nguoi_dung"
    __table_args__ = {"schema": "tuyensinh"}
    ma_nguoi_dung = Column(Integer, primary_key=True)
    ho_ten = Column(String(100), nullable=False)
    ten_dang_nhap = Column(String(50), unique=True, nullable=False)
    mat_khau = Column(String(255), nullable=False)
    vai_tro = Column(String(30), nullable=False)

class HoSo(Base):
    __tablename__ = "ho_so"
    __table_args__ = {"schema": "tuyensinh"}
    ma_ho_so = Column(Integer, primary_key=True)
    ma_thi_sinh = Column(Integer, ForeignKey("tuyensinh.thi_sinh.ma_thi_sinh"), nullable=False)
    ma_nguoi_dung = Column(Integer, ForeignKey("tuyensinh.nguoi_dung.ma_nguoi_dung"))
    ngay_nop = Column(DateTime, default=datetime.utcnow, nullable=False)
    trang_thai = Column(String(30), default="CHO_XU_LY", nullable=False)
    qr_hash = Column(String(255), unique=True)
    thi_sinh = relationship("ThiSinh", back_populates="ho_so")
    nguoi_dung = relationship("NguoiDung")
    giay_to = relationship("GiayTo", back_populates="ho_so", cascade="all, delete-orphan")
    canh_bao = relationship("CanhBao", back_populates="ho_so", cascade="all, delete-orphan")

class LoaiGiayTo(Base):
    __tablename__ = "loai_giay_to"
    __table_args__ = {"schema": "tuyensinh"}
    ma_loai = Column(Integer, primary_key=True)
    ten_loai = Column(String(100), unique=True, nullable=False)
    giay_to = relationship("GiayTo", back_populates="loai")

class GiayTo(Base):
    __tablename__ = "giay_to"
    __table_args__ = {"schema": "tuyensinh"}
    ma_giay_to = Column(Integer, primary_key=True)
    ma_ho_so = Column(Integer, ForeignKey("tuyensinh.ho_so.ma_ho_so"), nullable=False)
    ma_loai = Column(Integer, ForeignKey("tuyensinh.loai_giay_to.ma_loai"), nullable=False)
    ten_file = Column(String(255), nullable=False)
    duong_dan = Column(String(255), nullable=False)
    chat_luong_anh = Column(String(50))
    ngay_tai_len = Column(DateTime, default=datetime.utcnow, nullable=False)
    ho_so = relationship("HoSo", back_populates="giay_to")
    loai = relationship("LoaiGiayTo", back_populates="giay_to")
    ocr_results = relationship("OCRResult", back_populates="giay_to", cascade="all, delete-orphan")

class OCRResult(Base):
    __tablename__ = "ocr_result"
    __table_args__ = {"schema": "tuyensinh"}
    ma_ocr = Column(Integer, primary_key=True)
    ma_giay_to = Column(Integer, ForeignKey("tuyensinh.giay_to.ma_giay_to"), nullable=False)
    truong_du_lieu = Column(String(100), nullable=False)
    gia_tri = Column(Text)
    do_tin_cay = Column(Float)
    giay_to = relationship("GiayTo", back_populates="ocr_results")

class CanhBao(Base):
    __tablename__ = "canh_bao"
    __table_args__ = {"schema": "tuyensinh"}
    ma_canh_bao = Column(Integer, primary_key=True)
    ma_ho_so = Column(Integer, ForeignKey("tuyensinh.ho_so.ma_ho_so"), nullable=False)
    loai_loi = Column(String(100), nullable=False)
    mo_ta = Column(Text)
    muc_do = Column(String(20), default="THAP", nullable=False)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False)
    ho_so = relationship("HoSo", back_populates="canh_bao")
