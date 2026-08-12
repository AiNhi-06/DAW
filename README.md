# QNU_TuyenSinh

Đây là bộ khung triển khai hệ thống hỗ trợ xét tuyển hồ sơ theo tài liệu dự án.

## Công nghệ
Streamlit + FastAPI + PostgreSQL/pgAdmin 4 + OpenCV + Pillow + PaddleOCR + Rule Engine.

## Cài đặt Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Tạo database trong pgAdmin 4:
`tuyen_sinh_qnu`

Chạy:
`database/schema.sql`

Tạo `.env` từ `.env.example` và điền mật khẩu PostgreSQL.

Backend:
```powershell
uvicorn backend.main:app --reload
```

Frontend:
```powershell
streamlit run frontend/app.py
```

Mở:
- Frontend: http://localhost:8501
- Backend: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## Tài khoản mẫu
Username: `admin`
Password: `admin123`

Tài khoản này chỉ dùng cho demo; cần đổi trước khi triển khai thật.

## Luồng xử lý
Upload → kiểm tra file → OpenCV/Pillow → OCR → lưu OCR_RESULT → Rule Engine → CANH_BAO → cán bộ xem xét → duyệt/từ chối.

Một số giá trị trạng thái và ngưỡng cảnh báo trong code là lựa chọn triển khai của prototype vì tài liệu gốc chỉ quy định kiểu dữ liệu, chưa quy định bộ giá trị chi tiết.
