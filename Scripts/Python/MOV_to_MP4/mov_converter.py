import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import subprocess
import threading
import queue
import os
import time

FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"
SUPPORTED_INPUT_FORMATS = ('.mov', '.webm', '.mkv', '.avi', '.flv', '.mpg', '.mpeg')

QUALITY_PRESETS = {
    "Fast (lower size)": ["-crf", "28", "-preset", "faster"],
    "Balanced (default)": ["-crf", "23", "-preset", "medium"],
    "High (large file)": ["-crf", "18", "-preset", "slow"]
}

animation_running = False

def convert_to_mp4(files, progress_queue, quality_args):
    total = len(files)
    for idx, file in enumerate(files):
        input_path = Path(file)
        if input_path.suffix.lower() not in SUPPORTED_INPUT_FORMATS:
            progress_queue.put((idx + 1, total, f"Skipped: {input_path.name}"))
            continue

        output_path = input_path.with_suffix('.mp4')

        try:
            progress_queue.put((idx + 1, total, f"Converting: {input_path.name}"))

            subprocess.run([
                FFMPEG_PATH,
                "-i", str(input_path),
                "-vcodec", "libx264",
                *quality_args,
                "-acodec", "aac",
                "-b:a", "128k",
                str(output_path)
            ], check=True)

        except FileNotFoundError:
            messagebox.showerror("Error", "ffmpeg not found.\nInstall via Homebrew:\nbrew install ffmpeg")
            break
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"ffmpeg failed:\n{e}")
            break

    progress_queue.put("DONE")

def animate_spinner(label):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    def update():
        nonlocal idx
        if animation_running:
            label.config(text=f"Working... {spinner[idx % len(spinner)]}")
            idx += 1
            label.after(100, update)
        else:
            label.config(text="Done.")
    update()

def main():
    root = tk.Tk()
    root.title("Video to MP4 Converter")
    root.geometry("440x300")
    root.resizable(False, False)

    tk.Label(root, text="Video to MP4 Converter", font=("Arial", 14)).pack(pady=10)

    spinner_label = tk.Label(root, text="Waiting for files...", font=("Arial", 10))
    spinner_label.pack()

    tk.Label(root, text="Select quality preset:", font=("Arial", 10)).pack()
    quality_var = tk.StringVar(value="Balanced (default)")
    quality_menu = ttk.Combobox(root, textvariable=quality_var, values=list(QUALITY_PRESETS.keys()), state="readonly")
    quality_menu.pack(pady=5)

    selected_files = []

    def select_files():
        nonlocal selected_files
        paths = filedialog.askopenfilenames(
            title="Select video files",
            filetypes=[("Video files", "*.mov *.webm *.mkv *.avi *.flv *.mpg *.mpeg")]
        )
        selected_files = paths
        spinner_label.config(text=f"{len(paths)} file(s) selected.")

    def start_conversion():
        global animation_running
        if not selected_files:
            messagebox.showwarning("No files", "Please select files first.")
            return
        selected = quality_var.get()
        quality_args = QUALITY_PRESETS[selected]
        progress_queue = queue.Queue()
        animation_running = True
        animate_spinner(spinner_label)

        def update_progress():
            try:
                while True:
                    item = progress_queue.get_nowait()
                    if item == "DONE":
                        messagebox.showinfo("Done", "Conversion finished.")
                        global animation_running
                        animation_running = False
                        return
            except queue.Empty:
                root.after(100, update_progress)

        threading.Thread(target=convert_to_mp4, args=(selected_files, progress_queue, quality_args)).start()
        update_progress()

    ttk.Button(root, text="Select files", command=select_files).pack(pady=5)
    ttk.Button(root, text="Start conversion", command=start_conversion).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
