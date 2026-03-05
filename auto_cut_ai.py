"""
Auto Cut AI - Tool ghép video tự động với FFmpeg
Ứng dụng Windows Desktop (Python + Tkinter)
"""

import os
import re
import json
import random
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


# Danh sách hiệu ứng xfade được hỗ trợ
XFADE_EFFECTS = [
    "fade", "fadeblack", "fadewhite", "distance",
    "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown",
    "smoothleft", "smoothright", "smoothup", "smoothdown",
    "circlecrop", "circleclose", "circleopen",
    "horzclose", "horzopen", "vertclose", "vertopen",
    "diagbl", "diagbr", "diagtl", "diagtr",
    "hlslice", "hrslice", "vuslice", "vdslice",
    "dissolve", "pixelize", "radial", "hblur",
    "wipetl", "wipetr", "wipebl", "wipebr",
    "squeezeh", "squeezev", "zoomin",
]

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}

# Cấu hình độ phân giải đầu ra
RESOLUTION_OPTIONS = {
    "Giữ nguyên": None,
    "1080p (1920x1080)": (1920, 1080),
    "2K (2560x1440)": (2560, 1440),
    "4K (3840x2160)": (3840, 2160),
}

# Timeout constants (seconds)
FFPROBE_TIMEOUT = 30
FFMPEG_TIMEOUT = 1800


def get_video_duration(video_path: str) -> float:
    """Lấy duration của video bằng ffprobe (giây)."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=FFPROBE_TIMEOUT)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffprobe lỗi khi đọc '{video_path}':\n{result.stderr.strip()}"
        )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def normalize_base_name(name: str) -> str:
    """
    Chuẩn hóa base name: thay khoảng trắng bằng dấu gạch nối,
    chuyển về chữ thường để so sánh nhóm.
    """
    return name.replace(" ", "-").lower()


def group_videos(folder: str) -> dict:
    """
    Quét folder, nhóm video theo tên.
    Pattern nhận dạng: tên_gốc.ext hoặc tên_gốc (N).ext
    Trả về dict: {base_name: [(index, filepath), ...]}
    Chỉ bao gồm nhóm có >= 2 file.
    """
    groups: dict[str, list] = {}

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            continue

        root, ext = os.path.splitext(filename)
        if ext.lower() not in VIDEO_EXTENSIONS:
            continue

        # Thử match pattern "tên (N)"
        m = re.match(r"^(.+?)\s*\((\d+)\)$", root)
        if m:
            raw_base = m.group(1).strip()
            index = int(m.group(2))
        else:
            raw_base = root.strip()
            index = 0

        norm = normalize_base_name(raw_base)

        if norm not in groups:
            # Lưu display name từ lần đầu gặp (ưu tiên file gốc index=0)
            groups[norm] = {"display": raw_base, "files": []}

        groups[norm]["files"].append((index, filepath))

    # Chỉ giữ nhóm có >= 2 file, sắp xếp theo index
    result = {}
    for norm, data in groups.items():
        if len(data["files"]) >= 2:
            sorted_files = sorted(data["files"], key=lambda x: x[0])
            result[data["display"]] = [fp for _, fp in sorted_files]

    return result


def merge_two_videos(
    video1: str,
    video2: str,
    output: str,
    transition: str,
    duration: float,
    log_callback,
    resolution: tuple = None,
) -> None:
    """
    Ghép 2 video với hiệu ứng xfade + acrossfade.
    resolution: tuple (width, height) hoặc None để giữ nguyên.
    """
    dur1 = get_video_duration(video1)
    offset = max(0.0, dur1 - duration)

    log_callback(
        f"  Ghép: {os.path.basename(video1)} + {os.path.basename(video2)}"
        f" | transition={transition} | offset={offset:.3f}s"
    )

    if resolution:
        w, h = resolution
        log_callback(f"  Nâng chất lượng: {w}x{h}")
        # Scale cả hai input lên cùng resolution trước khi xfade
        # Sử dụng lanczos cho chất lượng upscale tốt nhất
        # force_original_aspect_ratio=decrease + pad để tránh méo hình
        scale_v0 = (
            f"[0:v]scale={w}:{h}:flags=lanczos:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"setsar=1[v0]"
        )
        scale_v1 = (
            f"[1:v]scale={w}:{h}:flags=lanczos:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"setsar=1[v1]"
        )
        # xfade giữa 2 video đã scale + unsharp để tăng độ nét
        xfade_part = (
            f"[v0][v1]xfade=transition={transition}"
            f":duration={duration}:offset={offset},"
            f"unsharp=5:5:0.5:5:5:0.5[vout]"
        )
        vf = f"{scale_v0};{scale_v1};{xfade_part}"
    else:
        # Không scale, chỉ xfade
        vf = (
            f"[0:v][1:v]xfade=transition={transition}"
            f":duration={duration}:offset={offset}[vout]"
        )

    # Audio filter: acrossfade
    af = (
        f"[0:a][1:a]acrossfade=d={duration}[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video1,
        "-i", video2,
        "-filter_complex", f"{vf};{af}",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
    ]

    # Thêm cấu hình chất lượng khi nâng độ phân giải
    if resolution:
        cmd.extend(["-crf", "18", "-preset", "slow", "-b:a", "192k"])

    cmd.extend([
        "-c:a", "aac",
        "-movflags", "+faststart",
        output,
    ])

    log_callback(f"  Lệnh FFmpeg: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=FFMPEG_TIMEOUT)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg lỗi khi ghép:\n{result.stderr[-2000:]}"
        )


def merge_video_group(
    group_name: str,
    video_files: list,
    output_folder: str,
    transitions: list,
    duration: float,
    log_callback,
    progress_callback,
    resolution: tuple = None,
) -> str:
    """
    Ghép tất cả video trong nhóm tuần tự.
    transitions: list N-1 tên hiệu ứng (tương ứng với N-1 đoạn nối).
    resolution: tuple (width, height) hoặc None để giữ nguyên.
    Trả về đường dẫn file output.
    """
    import tempfile

    tmp_files = []
    current = video_files[0]

    for i, next_video in enumerate(video_files[1:]):
        transition = transitions[i]
        is_last = (i == len(video_files) - 2)

        if is_last:
            # Xuất thẳng ra output cuối cùng
            safe_name = re.sub(r'[\\/:*?"<>|]', "_", group_name)
            output_path = os.path.join(output_folder, f"{safe_name}.mp4")
        else:
            # File trung gian tạm
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4", prefix="autocut_tmp_")
            os.close(tmp_fd)
            tmp_files.append(tmp_path)
            output_path = tmp_path

        merge_two_videos(
            current, next_video, output_path,
            transition, duration, log_callback, resolution
        )
        current = output_path
        progress_callback()

    # Dọn dẹp tất cả file tạm trung gian (final output được tạo riêng)
    for tmp in tmp_files:
        try:
            os.remove(tmp)
        except OSError:
            pass

    return current


class AutoCutAI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Cut AI - Ghép Video Tự Động")
        self.geometry("900x700")
        self.resizable(True, True)

        self._groups: dict = {}  # {group_name: [file_paths]}
        self._transition_vars: list[tk.StringVar] = []
        self._random_var = tk.BooleanVar(value=False)
        self._duration_var = tk.DoubleVar(value=1.0)
        self._resolution_var = tk.StringVar(value="Giữ nguyên")
        self._input_var = tk.StringVar()
        self._output_var = tk.StringVar()
        self._is_processing = False

        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # ── Folder chọn ──────────────────────────────────────────────
        folder_frame = ttk.LabelFrame(self, text="Cài đặt thư mục", padding=6)
        folder_frame.pack(fill="x", **pad)

        ttk.Label(folder_frame, text="Thư mục Input:").grid(
            row=0, column=0, sticky="w", padx=4, pady=2
        )
        ttk.Entry(folder_frame, textvariable=self._input_var, width=60).grid(
            row=0, column=1, sticky="ew", padx=4, pady=2
        )
        ttk.Button(
            folder_frame, text="Browse…", command=self._browse_input
        ).grid(row=0, column=2, padx=4, pady=2)

        ttk.Label(folder_frame, text="Thư mục Output:").grid(
            row=1, column=0, sticky="w", padx=4, pady=2
        )
        ttk.Entry(folder_frame, textvariable=self._output_var, width=60).grid(
            row=1, column=1, sticky="ew", padx=4, pady=2
        )
        ttk.Button(
            folder_frame, text="Browse…", command=self._browse_output
        ).grid(row=1, column=2, padx=4, pady=2)

        folder_frame.columnconfigure(1, weight=1)

        # ── Nút quét ─────────────────────────────────────────────────
        scan_frame = ttk.Frame(self)
        scan_frame.pack(fill="x", **pad)
        ttk.Button(
            scan_frame, text="🔍  Quét Video", command=self._scan_videos, width=20
        ).pack(side="left", padx=4)

        # ── Danh sách nhóm + cấu hình transition ─────────────────────
        self._groups_outer = ttk.LabelFrame(
            self, text="Danh sách nhóm video & Cấu hình Transition", padding=6
        )
        self._groups_outer.pack(fill="both", expand=True, **pad)

        # Canvas + scrollbar để scroll danh sách nhóm
        canvas = tk.Canvas(self._groups_outer, borderwidth=0)
        vsb = ttk.Scrollbar(
            self._groups_outer, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._groups_frame = ttk.Frame(canvas)
        self._canvas_window = canvas.create_window(
            (0, 0), window=self._groups_frame, anchor="nw"
        )
        self._groups_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(
                self._canvas_window, width=e.width
            ),
        )
        self._canvas = canvas

        # ── Cài đặt ghép ─────────────────────────────────────────────
        settings_frame = ttk.LabelFrame(self, text="Cài đặt ghép", padding=6)
        settings_frame.pack(fill="x", **pad)

        ttk.Label(settings_frame, text="Thời gian transition (giây):").grid(
            row=0, column=0, sticky="w", padx=4, pady=2
        )
        ttk.Spinbox(
            settings_frame,
            textvariable=self._duration_var,
            from_=0.1,
            to=5.0,
            increment=0.1,
            width=8,
            format="%.1f",
        ).grid(row=0, column=1, sticky="w", padx=4, pady=2)

        ttk.Checkbutton(
            settings_frame,
            text="Random hiệu ứng cho tất cả đoạn nối",
            variable=self._random_var,
            command=self._on_random_toggle,
        ).grid(row=0, column=2, sticky="w", padx=20, pady=2)

        ttk.Label(settings_frame, text="Độ phân giải đầu ra:").grid(
            row=1, column=0, sticky="w", padx=4, pady=2
        )
        ttk.Combobox(
            settings_frame,
            textvariable=self._resolution_var,
            values=list(RESOLUTION_OPTIONS.keys()),
            state="readonly",
            width=20,
        ).grid(row=1, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(
            settings_frame,
            text="(Chọn 1080p/2K/4K để nâng cao chất lượng video)",
            foreground="gray",
        ).grid(row=1, column=2, sticky="w", padx=20, pady=2)

        # ── Progress + Nút bắt đầu ───────────────────────────────────
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", **pad)

        self._progress_var = tk.DoubleVar(value=0)
        self._progress_bar = ttk.Progressbar(
            action_frame,
            variable=self._progress_var,
            maximum=100,
            length=600,
            mode="determinate",
        )
        self._progress_bar.pack(side="left", fill="x", expand=True, padx=4)

        self._start_btn = ttk.Button(
            action_frame,
            text="▶  Bắt đầu ghép",
            command=self._start_merge,
            width=18,
        )
        self._start_btn.pack(side="right", padx=4)

        # ── Log area ─────────────────────────────────────────────────
        log_frame = ttk.LabelFrame(self, text="Log xử lý", padding=4)
        log_frame.pack(fill="both", expand=False, **pad)

        self._log_text = scrolledtext.ScrolledText(
            log_frame, height=10, state="disabled", wrap="word",
            font=("Consolas", 9),
        )
        self._log_text.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Browse helpers
    # ------------------------------------------------------------------

    def _browse_input(self):
        path = filedialog.askdirectory(title="Chọn thư mục Input")
        if path:
            self._input_var.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Chọn thư mục Output")
        if path:
            self._output_var.set(path)

    # ------------------------------------------------------------------
    # Scan videos
    # ------------------------------------------------------------------

    def _scan_videos(self):
        folder = self._input_var.get().strip()
        if not folder:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn thư mục Input.")
            return
        if not os.path.isdir(folder):
            messagebox.showerror("Lỗi", f"Thư mục không tồn tại:\n{folder}")
            return

        self._log(f"Đang quét thư mục: {folder}")
        try:
            groups = group_videos(folder)
        except Exception as exc:
            messagebox.showerror("Lỗi quét", str(exc))
            return

        self._groups = groups
        self._rebuild_groups_ui()

        if not groups:
            self._log("Không tìm thấy nhóm video nào (cần >= 2 file cùng nhóm).")
        else:
            self._log(f"Tìm thấy {len(groups)} nhóm video.")
            for name, files in groups.items():
                self._log(f"  • {name}: {len(files)} file")

    def _rebuild_groups_ui(self):
        """Xây dựng lại UI danh sách nhóm và dropdown transition."""
        for widget in self._groups_frame.winfo_children():
            widget.destroy()
        self._transition_vars.clear()

        if not self._groups:
            ttk.Label(
                self._groups_frame,
                text="(Chưa có nhóm nào — hãy nhấn 'Quét Video')",
                foreground="gray",
            ).pack(padx=8, pady=8)
            return

        for group_name, files in self._groups.items():
            grp_lf = ttk.LabelFrame(
                self._groups_frame,
                text=f"Nhóm: {group_name}  ({len(files)} video)",
                padding=4,
            )
            grp_lf.pack(fill="x", padx=4, pady=3)

            # Danh sách file
            for i, fp in enumerate(files):
                ttk.Label(
                    grp_lf,
                    text=f"  [{i}] {os.path.basename(fp)}",
                    foreground="#333",
                ).grid(row=i, column=0, sticky="w", padx=4)

            # Dropdown transition cho mỗi đoạn nối
            n_joins = len(files) - 1
            for j in range(n_joins):
                row_offset = len(files) + j
                ttk.Label(
                    grp_lf,
                    text=f"  Nối [{j}]→[{j+1}] transition:",
                ).grid(row=row_offset, column=0, sticky="w", padx=4, pady=1)

                var = tk.StringVar(value=XFADE_EFFECTS[0])
                self._transition_vars.append(var)

                cb = ttk.Combobox(
                    grp_lf,
                    textvariable=var,
                    values=XFADE_EFFECTS,
                    state="readonly",
                    width=20,
                )
                cb.grid(row=row_offset, column=1, sticky="w", padx=4, pady=1)

            grp_lf.columnconfigure(1, weight=1)

        # Áp dụng trạng thái random hiện tại
        self._on_random_toggle()

    # ------------------------------------------------------------------
    # Random toggle
    # ------------------------------------------------------------------

    def _on_random_toggle(self):
        state = "disabled" if self._random_var.get() else "readonly"
        for widget in self._groups_frame.winfo_descendants():
            if isinstance(widget, ttk.Combobox):
                widget.configure(state=state)

    # ------------------------------------------------------------------
    # Start merge
    # ------------------------------------------------------------------

    def _start_merge(self):
        if self._is_processing:
            return

        if not self._groups:
            messagebox.showwarning(
                "Chưa quét video",
                "Vui lòng quét video trước khi ghép."
            )
            return

        output_folder = self._output_var.get().strip()
        if not output_folder:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn thư mục Output.")
            return
        os.makedirs(output_folder, exist_ok=True)

        duration = self._duration_var.get()
        use_random = self._random_var.get()
        resolution = RESOLUTION_OPTIONS[self._resolution_var.get()]

        # Thu thập transitions cho từng nhóm
        groups_transitions: list[tuple[str, list, list]] = []
        var_idx = 0
        for group_name, files in self._groups.items():
            n_joins = len(files) - 1
            if use_random:
                transitions = [random.choice(XFADE_EFFECTS) for _ in range(n_joins)]
            else:
                transitions = [
                    self._transition_vars[var_idx + k].get()
                    for k in range(n_joins)
                ]
            var_idx += n_joins
            groups_transitions.append((group_name, files, transitions))

        # Tổng số bước (mỗi đoạn nối = 1 bước)
        total_steps = sum(len(files) - 1 for _, files, _ in groups_transitions)
        self._progress_var.set(0)
        self._completed_steps = 0
        self._total_steps = total_steps

        self._is_processing = True
        self._start_btn.configure(state="disabled")
        self._log("=" * 50)
        self._log("Bắt đầu ghép video...")
        if resolution:
            self._log(f"Độ phân giải đầu ra: {resolution[0]}x{resolution[1]}")

        thread = threading.Thread(
            target=self._merge_worker,
            args=(groups_transitions, output_folder, duration, resolution),
            daemon=True,
        )
        thread.start()

    def _merge_worker(self, groups_transitions, output_folder, duration, resolution):
        errors = []
        for group_name, files, transitions in groups_transitions:
            self._log(f"\n▶ Đang ghép nhóm: {group_name}")
            try:
                out = merge_video_group(
                    group_name=group_name,
                    video_files=files,
                    output_folder=output_folder,
                    transitions=transitions,
                    duration=duration,
                    log_callback=self._log,
                    progress_callback=self._step_done,
                    resolution=resolution,
                )
                self._log(f"✅ Hoàn thành: {out}")
            except Exception as exc:
                msg = f"❌ Lỗi nhóm '{group_name}': {exc}"
                self._log(msg)
                errors.append(msg)

        self.after(0, self._merge_done, errors)

    def _step_done(self):
        self._completed_steps += 1
        pct = (self._completed_steps / self._total_steps) * 100
        self.after(0, lambda: self._progress_var.set(pct))

    def _merge_done(self, errors):
        self._is_processing = False
        self._start_btn.configure(state="normal")
        self._progress_var.set(100)
        self._log("\n" + "=" * 50)
        if errors:
            self._log(f"Hoàn tất với {len(errors)} lỗi.")
            messagebox.showwarning(
                "Hoàn tất (có lỗi)",
                f"Ghép xong nhưng có {len(errors)} lỗi.\nKiểm tra log để biết chi tiết.",
            )
        else:
            self._log("✅ Ghép tất cả nhóm thành công!")
            messagebox.showinfo("Hoàn tất", "Ghép tất cả video thành công!")

    # ------------------------------------------------------------------
    # Log helper (thread-safe via after())
    # ------------------------------------------------------------------

    def _log(self, message: str):
        def _append():
            self._log_text.configure(state="normal")
            self._log_text.insert("end", message + "\n")
            self._log_text.see("end")
            self._log_text.configure(state="disabled")

        # Nếu đang ở main thread, gọi trực tiếp; ngược lại dùng after()
        try:
            self.after(0, _append)
        except RuntimeError:
            pass


def main():
    app = AutoCutAI()
    app.mainloop()


if __name__ == "__main__":
    main()
