# 🎬 Auto Cut AI

> **Tool ghép video tự động với hiệu ứng chuyển cảnh (transition) sử dụng FFmpeg**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![FFmpeg](https://img.shields.io/badge/FFmpeg-required-green?logo=ffmpeg)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## 📋 Mô tả

**Auto Cut AI** là ứng dụng desktop (Python + Tkinter) giúp bạn tự động ghép nhiều đoạn video thành một video hoàn chỉnh với các hiệu ứng chuyển cảnh đẹp mắt, hoàn toàn miễn phí và không giới hạn.

Hỗ trợ **nâng cao chất lượng video** lên 1080p, 2K hoặc 4K với bộ lọc làm sắc nét (unsharp) và thuật toán upscale Lanczos. Có thể **đóng gói thành file .exe** để chạy trực tiếp trên Windows.

Ứng dụng tự động **nhận diện và nhóm** các file video cùng tên, sau đó ghép chúng lại theo thứ tự với hiệu ứng `xfade` của FFmpeg.

---

## 🖥️ Giao diện ứng dụng

```
┌─────────────────────────────────────────────────────────────┐
│  Auto Cut AI - Ghép Video Tự Động                           │
├─────────────────────────────────────────────────────────────┤
│  Thư mục Input:  [___________________________] [Browse…]    │
│  Thư mục Output: [___________________________] [Browse…]    │
│                                                             │
│  [🔍 Quét Video]                                            │
├─────────────────────────────────────────────────────────────┤
│  Danh sách nhóm video & Cấu hình Transition                 │
│  ┌─ Nhóm: video-1 (3 video) ──────────────────────────┐    │
│  │  [0] video-1.mp4                                    │    │
│  │  [1] video-1 (1).mp4                               │    │
│  │  [2] video-1 (2).mp4                               │    │
│  │  Nối [0]→[1] transition: [fade          ▼]         │    │
│  │  Nối [1]→[2] transition: [wipeleft      ▼]         │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Thời gian transition: [1.0 ▲▼]  ☑ Random hiệu ứng         │
│  Độ phân giải đầu ra:  [1080p (1920x1080) ▼]               │
│  [████████████░░░░░░░░░] 60%        [▶ Bắt đầu ghép]       │
├─────────────────────────────────────────────────────────────┤
│  Log xử lý:                                                 │
│  > Đang ghép nhóm: video-1                                  │
│  >   Ghép: video-1.mp4 + video-1 (1).mp4 | fade | ...      │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|---|---|
| Python | 3.8+ |
| FFmpeg | 4.3+ (có `xfade` filter) |
| Tkinter | Đi kèm Python (built-in) |
| RAM | 512 MB+ |
| OS | Windows 10+, macOS 10.15+, Ubuntu 20.04+ |

---

## 🔧 Cài đặt FFmpeg

### Windows

1. Truy cập: https://www.gyan.dev/ffmpeg/builds/
2. Tải bản **ffmpeg-release-full.7z**
3. Giải nén vào `C:\ffmpeg\`
4. Thêm `C:\ffmpeg\bin` vào **System PATH**:
   - Tìm kiếm **"Environment Variables"** trong Start Menu
   - Chọn **Path** → **Edit** → **New** → nhập `C:\ffmpeg\bin`
5. Kiểm tra: mở CMD → gõ `ffmpeg -version`

### macOS

```bash
# Cài Homebrew nếu chưa có
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Cài FFmpeg
brew install ffmpeg

# Kiểm tra
ffmpeg -version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg

# Kiểm tra
ffmpeg -version
```

---

## 🚀 Cài đặt & Chạy ứng dụng

### 1. Clone repository

```bash
git clone https://github.com/Langvan203/auto-cut-ai.git
cd auto-cut-ai
```

### 2. (Tuỳ chọn) Tạo môi trường ảo

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Chạy ứng dụng

```bash
python auto_cut_ai.py
```

> **Lưu ý:** Không cần cài thêm package Python nào. Ứng dụng chỉ dùng thư viện built-in (tkinter, subprocess, threading, ...).

---

## 📖 Hướng dẫn sử dụng

### Bước 1: Chuẩn bị video

Đặt các file video vào một thư mục. Đặt tên theo quy tắc nhóm (xem bên dưới).

### Bước 2: Chọn thư mục

- Nhấn **Browse…** cạnh **Thư mục Input** → chọn thư mục chứa video gốc.
- Nhấn **Browse…** cạnh **Thư mục Output** → chọn nơi lưu video đã ghép.

### Bước 3: Quét video

Nhấn **🔍 Quét Video** — ứng dụng sẽ tự động phát hiện và nhóm các file video.

### Bước 4: Cấu hình hiệu ứng & chất lượng

- Với mỗi nhóm, chọn hiệu ứng transition cho từng đoạn nối bằng dropdown.
- Hoặc tích chọn **Random hiệu ứng** để hệ thống tự chọn ngẫu nhiên.
- Điều chỉnh **Thời gian transition** (mặc định 1.0 giây).
- Chọn **Độ phân giải đầu ra** để nâng cao chất lượng video:
  - **Giữ nguyên** — giữ resolution gốc.
  - **1080p (1920×1080)** — Full HD.
  - **2K (2560×1440)** — QHD.
  - **4K (3840×2160)** — Ultra HD.

### Bước 5: Ghép video

Nhấn **▶ Bắt đầu ghép** và theo dõi tiến trình trong progress bar và log.

---

## 📁 Quy tắc nhóm video

Ứng dụng tự động nhận diện các file theo pattern:

| File name | Base name | Thứ tự |
|---|---|---|
| `video-1.mp4` | `video-1` | 0 (gốc) |
| `video-1 (1).mp4` | `video-1` | 1 |
| `video-1 (2).mp4` | `video-1` | 2 |
| `video 1 (1).mp4` | `video-1` | 1 |
| `My Clip.mp4` | `My Clip` | 0 (gốc) |
| `My Clip (1).mp4` | `My Clip` | 1 |

> **Lưu ý:** Khoảng trắng và dấu gạch nối trong tên được xử lý tương đương nhau. Chỉ nhóm khi có **>= 2 file** cùng nhóm.

**Ví dụ cấu trúc thư mục:**

```
input/
├── video-1.mp4          ← base: video-1, index 0
├── video-1 (1).mp4      ← base: video-1, index 1
├── video-1 (2).mp4      ← base: video-1, index 2
├── my-clip.mp4          ← base: my-clip, index 0
└── my-clip (1).mp4      ← base: my-clip, index 1
```

Kết quả sẽ tạo ra:
```
output/
├── video-1.mp4    ← ghép từ 3 file
└── my-clip.mp4   ← ghép từ 2 file
```

---

## 🎨 Danh sách hiệu ứng Transition

| Nhóm | Hiệu ứng |
|---|---|
| **Fade** | `fade`, `fadeblack`, `fadewhite` |
| **Wipe** | `wipeleft`, `wiperight`, `wipeup`, `wipedown`, `wipetl`, `wipetr`, `wipebl`, `wipebr` |
| **Slide** | `slideleft`, `slideright`, `slideup`, `slidedown` |
| **Smooth** | `smoothleft`, `smoothright`, `smoothup`, `smoothdown` |
| **Circle** | `circlecrop`, `circleclose`, `circleopen` |
| **Horizontal/Vertical** | `horzclose`, `horzopen`, `vertclose`, `vertopen` |
| **Diagonal** | `diagbl`, `diagbr`, `diagtl`, `diagtr` |
| **Slice** | `hlslice`, `hrslice`, `vuslice`, `vdslice` |
| **Đặc biệt** | `dissolve`, `pixelize`, `radial`, `hblur`, `distance`, `squeezeh`, `squeezev`, `zoomin` |

> Tổng cộng **42 hiệu ứng** transition được hỗ trợ.

---

## 🎯 Nâng cao chất lượng video

Khi chọn độ phân giải đầu ra (1080p / 2K / 4K), ứng dụng sẽ tự động:

1. **Upscale** video bằng thuật toán **Lanczos** — cho chất lượng upscale tốt nhất
2. **Pad** letterbox tự động nếu tỉ lệ khung hình khác nhau (tránh méo hình)
3. **Unsharp masking** — bộ lọc làm sắc nét để video rõ ràng hơn sau khi upscale
4. **CRF 18 + preset slow** — chất lượng encoding cao (gần như lossless)
5. **Audio 192kbps AAC** — âm thanh chất lượng cao

| Độ phân giải | Kích thước | Ghi chú |
|---|---|---|
| Giữ nguyên | Theo video gốc | Không scale, không sharpen |
| 1080p | 1920×1080 | Full HD, phù hợp đa số |
| 2K | 2560×1440 | QHD, sắc nét hơn |
| 4K | 3840×2160 | Ultra HD, chất lượng cao nhất |

> **Lưu ý:** Video 4K sẽ tốn thời gian xử lý lâu hơn và dung lượng file lớn hơn đáng kể.

---

## 📦 Đóng gói thành file .exe

Bạn có thể đóng gói ứng dụng thành một file `.exe` duy nhất để chạy trực tiếp trên Windows mà không cần cài Python.

### 1. Cài đặt PyInstaller

```bash
pip install pyinstaller
```

### 2. Chạy script đóng gói

```bash
python build_exe.py
```

### 3. Kết quả

File `AutoCutAI.exe` sẽ nằm trong thư mục `dist/`. Copy file này ra bất kỳ đâu để sử dụng.

> **Lưu ý:** Máy chạy file `.exe` vẫn cần có **FFmpeg** đã cài đặt và có trong system PATH.

---

## ❓ FAQ / Xử lý lỗi thường gặp

### ❌ `ffmpeg` không được nhận ra (not found)

**Nguyên nhân:** FFmpeg chưa được cài hoặc chưa thêm vào PATH.

**Giải quyết:** Xem lại mục [Cài đặt FFmpeg](#-cài-đặt-ffmpeg) và đảm bảo lệnh `ffmpeg -version` chạy được trong terminal/CMD.

---

### ❌ Lỗi `xfade` filter

**Nguyên nhân:** Phiên bản FFmpeg cũ hơn 4.3 chưa hỗ trợ `xfade`.

**Giải quyết:** Cập nhật FFmpeg lên phiên bản mới nhất.

---

### ❌ Video output không có âm thanh

**Nguyên nhân:** Một hoặc nhiều video đầu vào không có audio track.

**Giải quyết:** Đảm bảo tất cả video trong nhóm đều có audio, hoặc thêm audio trống trước khi ghép.

---

### ❌ Không tìm thấy nhóm nào sau khi quét

**Nguyên nhân:** Tên file không đúng quy tắc hoặc chỉ có 1 file trong nhóm.

**Giải quyết:** Đổi tên file theo quy tắc `tên.ext` và `tên (1).ext`, `tên (2).ext`, ...

---

### ❌ GUI bị đơ khi ghép

**Mô tả:** Đây là trạng thái bình thường — video processing chạy trong background thread. GUI vẫn responsive, chỉ nút "Bắt đầu ghép" bị disable trong quá trình xử lý.

---

## 📂 Cấu trúc dự án

```
auto-cut-ai/
├── auto_cut_ai.py    # Ứng dụng chính
├── build_exe.py      # Script đóng gói thành file .exe
├── requirements.txt  # Dependencies (pyinstaller cho đóng gói)
├── README.md         # Hướng dẫn này
├── LICENSE           # MIT License
└── .gitignore
```

---

## 📄 License

[MIT License](LICENSE) — Copyright © 2026 Langvan203
