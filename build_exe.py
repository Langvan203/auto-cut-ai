"""
Script đóng gói Auto Cut AI thành file .exe bằng PyInstaller.

Cách sử dụng:
    pip install pyinstaller
    python build_exe.py

Kết quả: file AutoCutAI.exe trong thư mục dist/
"""

import subprocess
import sys


def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "AutoCutAI",
        "--clean",
        "auto_cut_ai.py",
    ]

    print("Đang đóng gói ứng dụng...")
    print(f"Lệnh: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ Đóng gói thành công!")
        print("File .exe nằm tại: dist/AutoCutAI.exe")
        print("\nLưu ý: Máy chạy file .exe cần có FFmpeg cài đặt trong PATH.")
    else:
        print("\n❌ Đóng gói thất bại. Kiểm tra log ở trên.")
        sys.exit(1)


if __name__ == "__main__":
    build()
