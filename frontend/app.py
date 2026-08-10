import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# CONFIG
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "static" / "Logo.png"

st.set_page_config(
    page_title="ĐH Quy Nhơn - Tuyển sinh",
    page_icon="🎓",
    layout="wide",
)

# STYLE
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        header[data-testid="stHeader"] {
            height: 0;
        }

        .main-title {
            text-align: center;
            color: #0b4f8a;
            font-size: 28px;
            font-weight: 700;
            margin: 25px 0 0 0;
        }

        .school-name {
            text-align: center;
            color: #555;
            font-size: 17px;
            font-weight: 600;
            margin: 0 0 12px 0;
        }

        h1, h2, h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }

        .stAlert {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        div[data-testid="stMetric"] {
            padding: 8px 10px;
        }

        .stButton button {
            border-radius: 6px;
        }

        section[data-testid="stSidebar"] {
            padding-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# HEADER
if LOGO.exists():
    st.image(str(LOGO), width="stretch")

st.markdown(
    '<div class="main-title">HỆ THỐNG HỖ TRỢ XÉT TUYỂN HỒ SƠ</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="school-name">TRƯỜNG ĐẠI HỌC QUY NHƠN</div>',
    unsafe_allow_html=True,
)

# SESSION
if "user" not in st.session_state:
    st.session_state.user = None

# API
def get(path):
    try:
        response = requests.get(
            API_URL + path,
            timeout=20,
        )

        if response.ok:
            return response.json()

        return None

    except requests.RequestException as e:
        st.error(f"Không kết nối được Backend: {e}")
        return None

# MENU
menu = st.sidebar.radio(
    "MENU", ["Trang chủ","Nộp hồ sơ", "Tra cứu hồ sơ","Cán bộ tuyển sinh",],
)

# TRANG CHỦ
if menu == "Trang chủ":
    st.info("Hệ thống tiếp nhận ảnh/PDF, tiền xử lý, OCR, chuẩn hóa, phát hiện cảnh báo và hỗ trợ cán bộ xem xét.")

# NỘP HỒ SƠ
elif menu == "Nộp hồ sơ":
    st.header("Nộp hồ sơ tuyển sinh")

    types = {
        1: "CCCD/CMND",
        2: "Học bạ/Bảng điểm",
        3: "Giấy chứng nhận tốt nghiệp",
        4: "Bằng tốt nghiệp",
        5: "Giấy tờ ưu tiên",
    }

    with st.form("nop_ho_so"):
        col1, col2 = st.columns(2)

        with col1:
            ho_ten = st.text_input("Họ và tên *")
            ngay_sinh = st.date_input("Ngày sinh",value=None,)
            gioi_tinh = st.selectbox("Giới tính",["", "Nam", "Nữ", "Khác"],)

        with col2:
            cccd = st.text_input("CCCD")
            email = st.text_input("Email")
            phone = st.text_input("Số điện thoại")

        st.markdown("**Giấy tờ hồ sơ**")

        selected_ids = []
        uploads = []

        cols = st.columns(2)

        for index, (i, label) in enumerate(types.items()):

            with cols[index % 2]:

                file = st.file_uploader(label,type=["jpg","jpeg","png","webp","pdf",],key=f"file_{i}",)

                if file:
                    selected_ids.append(i)
                    uploads.append(file)

        submit = st.form_submit_button("NỘP HỒ SƠ",width="stretch",)

    if submit:
        if not ho_ten.strip():
            st.error("Vui lòng nhập họ tên.")
        elif not uploads:
            st.error("Vui lòng tải ít nhất một giấy tờ.")
        else:
            data = {
                "ho_ten": ho_ten.strip(),
                "ngay_sinh": (
                    ngay_sinh.isoformat()
                    if ngay_sinh
                    else ""
                ),
                "gioi_tinh": gioi_tinh,
                "cccd": cccd.strip(),
                "email": email.strip(),
                "so_dien_thoai": phone.strip(),
                "ma_loai": [
                    str(x)
                    for x in selected_ids
                ],
            }

            file_payload = [
                ( "files",
                    (
                        f.name,
                        f.getvalue(),
                        f.type or "application/octet-stream",
                    ),
                )
                for f in uploads
            ]

            try:
                response = requests.post(
                    API_URL + "/api/ho-so/nop",
                    data=data,
                    files=file_payload,
                    timeout=180,
                )
                if response.ok:
                    result = response.json()

                    st.success(
                        f"Nộp thành công. "
                        f"Mã hồ sơ: {result.get('ma_ho_so')}"
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        st.write("**Mã tra cứu:**", result.get("qr_hash", ""),)
                        st.write( "**Trạng thái:**", result.get("trang_thai", ""),)
                    with c2:
                        try:
                            import qrcode
                            qr = qrcode.make(
                                str(result.get("qr_hash","",))
                            )

                            st.image(
                                qr,
                                caption="QR truy vết hồ sơ",
                                width=160,
                            )

                        except Exception:
                            pass

                    warnings = result.get(
                        "canh_bao",
                        [],
                    )

                    if warnings:

                        st.warning(
                            f"Phát hiện "
                            f"{result.get('so_canh_bao', len(warnings))} "
                            "cảnh báo."
                        )

                        for warning in warnings:

                            level = warning.get(
                                "level",
                                warning.get(
                                    "muc_do",
                                    "WARNING",
                                ),
                            )

                            description = warning.get(
                                "description",
                                warning.get(
                                    "mo_ta",
                                    "",
                                ),
                            )

                            st.write(
                                f"- [{level}] {description}"
                            )

                    else:

                        st.success(
                            "Không phát hiện cảnh báo."
                        )

                else:

                    st.error(
                        f"Lỗi từ Backend: {response.text}"
                    )

            except requests.RequestException as e:

                st.error(
                    f"Không thể gửi hồ sơ: {e}"
                )


# =========================
# TRA CỨU
# =========================

elif menu == "Tra cứu hồ sơ":

    st.header("Tra cứu hồ sơ")

    col1, col2 = st.columns([3, 1])

    with col1:
        ma = st.number_input(
            "Mã hồ sơ",
            min_value=1,
            step=1,
        )

    with col2:
        st.write("")
        st.write("")

        search = st.button(
            "TRA CỨU",
            width="stretch",
        )

    if search:

        result = get(
            f"/api/ho-so/{ma}"
        )

        if not result:

            st.error("Không tìm thấy hồ sơ.")

        else:

            st.success(
                f"Hồ sơ #{result.get('ma_ho_so')} — "
                f"{result.get('trang_thai')}"
            )

            thi_sinh = result.get(
                "thi_sinh",
                {},
            )

            c1, c2 = st.columns(2)

            with c1:
                st.write(
                    "**Thí sinh:**",
                    thi_sinh.get("ho_ten", ""),
                )

            with c2:
                st.write(
                    "**Mã tra cứu:**",
                    result.get("qr_hash", ""),
                )

            st.subheader("Giấy tờ")

            documents = result.get(
                "giay_to",
                [],
            )

            if documents:

                for document in documents:

                    st.write(
                        f"- {document.get('loai', '')}: "
                        f"{document.get('ten_file', '')} — "
                        f"{document.get('chat_luong_anh', '')}"
                    )

            else:

                st.info(
                    "Không có thông tin giấy tờ."
                )

            st.subheader("Cảnh báo")

            warnings = result.get(
                "canh_bao",
                [],
            )

            if warnings:

                for warning in warnings:

                    level = warning.get(
                        "muc_do",
                        warning.get(
                            "level",
                            "WARNING",
                        ),
                    )

                    description = warning.get(
                        "mo_ta",
                        warning.get(
                            "description",
                            "",
                        ),
                    )

                    st.warning(
                        f"[{level}] {description}"
                    )

            else:

                st.success(
                    "Không có cảnh báo."
                )


# =========================
# CÁN BỘ TUYỂN SINH
# =========================

else:

    if not st.session_state.user:

        st.header(
            "Đăng nhập cán bộ tuyển sinh"
        )

        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Tên đăng nhập"
            )

        with col2:
            password = st.text_input(
                "Mật khẩu",
                type="password",
            )

        if st.button(
            "ĐĂNG NHẬP",
            width="stretch",
        ):

            try:

                response = requests.post(
                    API_URL + "/api/auth/login",
                    json={
                        "ten_dang_nhap": username,
                        "mat_khau": password,
                    },
                    timeout=20,
                )

                if response.ok:

                    st.session_state.user = (
                        response.json()
                    )

                    st.rerun()

                else:

                    st.error(
                        "Sai tài khoản hoặc mật khẩu."
                    )

            except requests.RequestException as e:

                st.error(
                    f"Không thể kết nối Backend: {e}"
                )

    else:

        user = st.session_state.user

        top1, top2 = st.columns([5, 1])

        with top1:
            st.success(
                f"Đang đăng nhập: "
                f"{user.get('ho_ten', '')}"
            )

        with top2:

            if st.button(
                "ĐĂNG XUẤT",
                width="stretch",
            ):

                st.session_state.user = None
                st.rerun()

        st.header(
            "Dashboard tuyển sinh"
        )

        stats = get(
            "/api/dashboard"
        ) or {}

        a, b, c, d, e = st.columns(5)

        a.metric(
            "Tổng hồ sơ",
            stats.get("tong", 0),
        )

        b.metric(
            "Chờ xử lý",
            stats.get("cho_xu_ly", 0),
        )

        c.metric(
            "Đã duyệt",
            stats.get("da_duyet", 0),
        )

        d.metric(
            "Từ chối",
            stats.get("tu_choi", 0),
        )

        e.metric(
            "Cần xem xét",
            stats.get("can_xem_xet", 0),
        )

        st.subheader(
            "Danh sách hồ sơ"
        )

        rows = get(
            "/api/ho-so"
        ) or []

        if rows:

            st.dataframe(
                pd.DataFrame(rows),
                width="stretch",
            )

            col1, col2 = st.columns([3, 1])

            with col1:

                ma = st.number_input(
                    "Mã hồ sơ cần xử lý",
                    min_value=1,
                    step=1,
                )

            with col2:

                st.write("")
                st.write("")

                detail_button = st.button(
                    "XEM CHI TIẾT",
                    width="stretch",
                )

            if detail_button:

                detail = get(
                    f"/api/ho-so/{ma}"
                )

                if detail:

                    st.json(detail)

                    status = st.selectbox(
                        "Trạng thái mới",
                        [
                            "CHO_XU_LY",
                            "DANG_XU_LY",
                            "CAN_BO_XEM_XET",
                            "DA_DUYET",
                            "TU_CHOI",
                        ],
                    )

                    if st.button(
                        "CẬP NHẬT",
                        width="stretch",
                    ):

                        try:

                            response = requests.patch(
                                API_URL
                                + f"/api/ho-so/{ma}/trang-thai",
                                params={
                                    "status": status
                                },
                                timeout=20,
                            )

                            if response.ok:

                                st.success(
                                    "Đã cập nhật trạng thái."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    response.text
                                )

                        except requests.RequestException as e:

                            st.error(
                                f"Lỗi kết nối Backend: {e}"
                            )

                else:
                    st.error(
                        "Không tìm thấy hồ sơ."
                    )
        else:
            st.info(
                "Chưa có hồ sơ."
            )