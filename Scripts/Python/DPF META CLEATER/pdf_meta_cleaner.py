#!/usr/bin/env python3
"""
PDF Meta Cleaner — інструмент для очищення PDF-файлів від метаданих
Мова інтерфейсу: суржик
Коментарі: російською
"""

# ============================
# 📦 Импорты и глобальные переменные
# ============================
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import random
import string
from shutil import copyfile, move

FLAG_FILE = os.path.expanduser("~/.pdfmeta_ok")

chosen_files = []
custom_metadata = None
entry_prefix = None  # поле ввода префикса
listbox_files = None  # список выбранных файлов

# ============================
# 🔧 Проверка зависимостей
# ============================
def libs_available():
    try:
        from PyPDF2 import PdfReader, PdfWriter
        try:
            from Crypto.Cipher import AES
        except ImportError:
            from Cryptodome.Cipher import AES
        return True
    except ImportError:
        return False

def install_libs_async(done_callback):
    def _worker():
        cmd = [sys.executable, "-m", "pip", "install", "--quiet",
               "PyPDF2", "pycryptodome", "pycryptodomex"]
        try:
            subprocess.check_call(cmd)
            ok = True
        except Exception:
            ok = False
        root.after(0, lambda: done_callback(ok))
    threading.Thread(target=_worker, daemon=True).start()

# ============================
# 🧠 Метаданные: генерация, загрузка, запись
# ============================
def scramble(text):
    return ''.join(c if not c.isalpha() else random.choice(string.ascii_letters) for c in text)

def generate_fake_metadata():
    return {"/Title": scramble("Untitled"), "/Author": scramble("Anonymous")}

def load_metadata_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return {f"/Custom{i}": line.strip() for i, line in enumerate(lines)}
    except:
        return generate_fake_metadata()

def wipe_and_replace_metadata(src_path, out_path, metadata):
    from PyPDF2 import PdfReader, PdfWriter
    reader = PdfReader(src_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata(metadata)
    with open(out_path, "wb") as f:
        writer.write(f)

# ============================
# 📂 Работа с файлами
# ============================
def choose_files():
    file_paths = filedialog.askopenfilenames(title="Вибери PDF-файли", filetypes=[("PDF файли", "*.pdf")])
    if file_paths:
        chosen_files.clear()
        chosen_files.extend(file_paths)
        update_listbox()

def choose_folder():
    folder = filedialog.askdirectory(title="Вибери папку з PDF")
    if folder:
        pdfs = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        chosen_files.clear()
        chosen_files.extend(pdfs)
        update_listbox()

def update_listbox():
    global listbox_files
    listbox_files.delete(0, tk.END)
    for f in chosen_files:
        listbox_files.insert(tk.END, os.path.basename(f))

def load_metadata():
    global custom_metadata
    meta_file = filedialog.askopenfilename(title="Завантаж .txt з метаданими", filetypes=[("Текстовий файл", "*.txt")])
    if meta_file:
        custom_metadata = load_metadata_from_file(meta_file)
        messagebox.showinfo("Метадані є", "Вони будуть застосовані до кожного PDF.")

# ============================
# 🧼 Очистка и обработка PDF
# ============================
def do_clean():
    global entry_prefix

    if not chosen_files:
        messagebox.showwarning("Немає файлів", "Спочатку вибери щось.")
        return

    prefix = entry_prefix.get().strip()
    if not prefix or not prefix.isdigit() or len(prefix) != 3:
        prefix = "000"

    metadata = custom_metadata if custom_metadata else generate_fake_metadata()
    base_dir = os.path.dirname(chosen_files[0])
    clean_dir = os.path.join(base_dir, prefix)
    os.makedirs(clean_dir, exist_ok=True)

    for src in chosen_files:
        base = os.path.basename(src)

        # Создаем путь для очищенного файла в целевой папке
        cleaned_name = f"{prefix}_{base}"
        cleaned_path = os.path.join(clean_dir, cleaned_name)

        # Копируем оригинал как есть
        copyfile(src, cleaned_path)
        wipe_and_replace_metadata(cleaned_path, cleaned_path, metadata)

    messagebox.showinfo("Готово", f"Очищено: {len(chosen_files)} файлів. Папка: {prefix}")
    chosen_files.clear()
    update_listbox()
    entry_prefix.delete(0, tk.END)

# ============================
# 🖥️ GUI интерфейс
# ============================
root = tk.Tk()
root.title("🧹 PDF Meta Cleaner")
root.geometry("400x460")
root.resizable(False, False)

tk.Label(root, text="Файли, які будеш чистити:").pack(pady=(10, 2))

listbox_files = tk.Listbox(root, height=10, width=50)
listbox_files.pack(pady=(0, 10))

btn_files = tk.Button(root, text="📂 Вибрати PDF файли", width=40, command=choose_files)
btn_files.pack(pady=2)

btn_folder = tk.Button(root, text="📁 Вибрати папку з PDF", width=40, command=choose_folder)
btn_folder.pack(pady=2)

btn_meta = tk.Button(root, text="📄 Завантажити .txt з метаданими", width=40, command=load_metadata)
btn_meta.pack(pady=2)

prefix_frame = tk.Frame(root)
prefix_frame.pack(pady=(10, 5))
tk.Label(prefix_frame, text="🔢 Префікс (3 цифри):").pack(side=tk.LEFT)
entry_prefix = tk.Entry(prefix_frame, width=5)
entry_prefix.insert(0, "000")
entry_prefix.pack(side=tk.LEFT, padx=5)

btn_clean = tk.Button(root, text="✖ Вичистити метадані ✖", width=40,
                      bg="#c62828", fg="white", font=("Helvetica", 12, "bold"),
                      command=do_clean)
btn_clean.pack(pady=15)

root.mainloop()