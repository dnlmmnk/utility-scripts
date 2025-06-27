import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import subprocess
import threading
import queue
import os

# Полный путь к ffmpeg (для Homebrew/macOS)
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"

def convert_mov_to_mp4(files, progress_queue):
    total = len(files)
    for idx, file in enumerate(files):
        input_path = Path(file)
        if input_path.suffix.lower() != '.mov':
            progress_queue.put((idx + 1, total, f"Пропущен: {input_path.name}"))
            continue

        output_path = input_path.with_suffix('.mp4')

        try:
            progress_queue.put((idx + 1, total, f"Конвертация: {input_path.name}"))

            subprocess.run([
                FFMPEG_PATH,
                "-i", str(input_path),
                "-vcodec", "libx264",
                "-crf", "23",
                "-preset", "medium",
                "-acodec", "aac",
                "-b:a", "128k",
                str(output_path)
            ], check=True)

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "ffmpeg не найден.\nУбедись, что он установлен через Homebrew:\nbrew install ffmpeg")
            break
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Ошибка", f"ffmpeg завершился с ошибкой:\n{e}")
            break

    progress_queue.put("DONE")

def choose_files(progress_label, progress_bar, root):
    file_paths = filedialog.askopenfilenames(
        title="Выбери MOV файлы",
        filetypes=[("MOV файлы", "*.mov")]
    )

    if not file_paths:
        messagebox.showwarning("Нет файлов", "Выбери хотя бы один .mov файл.")
        return

    progress_queue = queue.Queue()

    def update_progress():
        try:
            while True:
                item = progress_queue.get_nowait()
                if item == "DONE":
                    messagebox.showinfo("Готово", "Конвертация завершена.")
                    root.destroy()
                    return
                index, total, message = item
                progress_label.config(text=message)
                progress_bar["value"] = (index / total) * 100
        except queue.Empty:
            root.after(100, update_progress)

    thread = threading.Thread(target=convert_mov_to_mp4, args=(file_paths, progress_queue))
    thread.start()
    update_progress()

def main():
    root = tk.Tk()
    root.title("MOV → MP4 Конвертер")
    root.geometry("420x200")
    root.resizable(False, False)

    tk.Label(root, text="MOV → MP4 Конвертер", font=("Arial", 14)).pack(pady=10)

    progress_label = tk.Label(root, text="Ожидаю выбор файлов", font=("Arial", 10))
    progress_label.pack()

    progress_bar = ttk.Progressbar(root, length=350, mode="determinate")
    progress_bar.pack(pady=10)

    tk.Button(
        root,
        text="Выбрать MOV файлы",
        command=lambda: choose_files(progress_label, progress_bar, root),
        bg="#4caf50",
        fg="white",
        font=("Arial", 12)
    ).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
