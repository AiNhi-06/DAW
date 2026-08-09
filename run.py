"""
Chạy toàn bộ ứng dụng (Frontend + Backend) chỉ với một lệnh:
    python run.py

Khởi động song song:
    - Backend  : FastAPI  -> http://localhost:8000  (API, tài liệu tại /docs)
    - Frontend : Streamlit -> http://localhost:8501 (giao diện web)

Nhấn Ctrl+C để dừng cả hai.
"""

import os
import signal
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

PROCESSES = []


def start(name, command):
    """Khởi động một tiến trình con và theo dõi để dừng cùng lúc."""
    print(f"\n[{name}] Đang khởi động: {' '.join(command)}")
    proc = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    PROCESSES.append((name, proc))
    return proc


def stop_all():
    print("\nĐang dừng các tiến trình...")
    for name, proc in PROCESSES:
        print(f"[{name}] Đang tắt...")
        try:
            proc.terminate()
        except Exception:
            pass
    for name, proc in PROCESSES:
        try:
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    print("Đã dừng toàn bộ.")


def main():
    print("=" * 60)
    print("  ỨNG DỤNG QUÉT DỮ LIỆU HỒ SƠ")
    print("=" * 60)

    # Khởi động Backend FastAPI trước
    backend = start("Backend (FastAPI)", [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--reload", "--port", "8000",
    ])

    # Khởi động Frontend Streamlit
    frontend = start("Frontend (Streamlit)", [
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
    ])

    print("\n" + "-" * 60)
    print("  Backend  : http://localhost:8000")
    print("  Frontend : http://localhost:8501")
    print("  Nhấn Ctrl+C để dừng cả hai server.")
    print("-" * 60)

    try:
        # Giữ chương trình chạy; nếu một tiến trình thoát thì dừng tất cả
        while True:
            for name, proc in PROCESSES:
                if proc.poll() is not None:
                    print(f"\n[{name}] đã thoát với mã {proc.returncode}.")
                    stop_all()
                    sys.exit(proc.returncode)
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()


if __name__ == "__main__":
    main()
