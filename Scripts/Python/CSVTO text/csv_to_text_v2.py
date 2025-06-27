import csv
import os
import uuid
from tkinter import Tk, filedialog, messagebox

# Функция для генерации имени пользователя, если почта отсутствует
def generate_username():
    return f"user_{uuid.uuid4().hex[:8]}"

# Функция для конвертации CSV в текст по строкам
def convert_csv_rows_to_text(csv_file_path, output_folder_path):
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)  # Читаем все строки в список

            if len(rows) < 2:
                messagebox.showwarning("Ошибка", "Файл должен содержать минимум две строки: вопросы и ответы.")
                return

            # Первая строка - это вопросы
            questions = rows[0]

            # Проходим по каждой строке с ответами, начиная со второй строки
            for i, row in enumerate(rows[1:], start=1):
                if len(row) < 2:
                    continue  # Пропускаем пустые строки, если они есть

                email = row[1] if row[1].strip() else generate_username()  # Второй столбец - это email или сгенерированное имя
                email = email.replace("@", "_at_").replace(".", "_dot_")  # Безопасное имя файла

                # Имя файла формируем на основе email
                output_file_name = os.path.join(output_folder_path, f"{email}_answers.txt")

                # Записываем вопросы и ответы в текстовый файл
                with open(output_file_name, 'w', encoding='utf-8') as txtfile:
                    for question, answer in zip(questions[2:], row[2:]):  # Пропускаем Timestamp и Email
                        txtfile.write(f"Вопрос: {question}\n")
                        txtfile.write(f"Ответ: {answer}\n\n")

                print(f"Ответы пользователя {email} сохранены в файл: {output_file_name}")

        messagebox.showinfo("Готово", "Конвертация завершена! Все файлы сохранены.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Функция для выбора CSV файла и папки для сохранения файлов
def run_conversion():
    root = Tk()
    root.withdraw()  # Скрываем главное окно Tkinter

    # Выбор CSV файла
    csv_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not csv_file_path:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите CSV файл.")
        return

    # Выбор папки для сохранения выходных файлов
    output_folder_path = filedialog.askdirectory()
    if not output_folder_path:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите папку для сохранения.")
        return

    # Запуск конвертации
    convert_csv_rows_to_text(csv_file_path, output_folder_path)

# Запуск приложения
run_conversion()
