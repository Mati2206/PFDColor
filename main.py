import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os
import sys
import subprocess

from PDFColor import PDFColor

class PDFColorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Color Changer")
        self.root.geometry("500x250")
        self.root.resizable(False, False)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.chosen_rgb_float = (1.0, 0.0, 1.0)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Plik PDF wejściowy:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.input_path, width=40).grid(row=0, column=1, padx=5, pady=10)
        tk.Button(self.root, text="Przeglądaj...", command=self.select_input_file).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Zapisz jako:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.output_path, width=40).grid(row=1, column=1, padx=5, pady=10)
        tk.Button(self.root, text="Zmień...", command=self.select_output_file).grid(row=1, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Kolor docelowy:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.color_preview = tk.Frame(self.root, width=40, height=25, bg="#ff00ff", relief="sunken", bd=2)
        self.color_preview.grid(row=2, column=1, padx=5, pady=10, sticky="w")
        tk.Button(self.root, text="Wybierz kolor", command=self.choose_color).grid(row=2, column=1, padx=60, pady=10, sticky="w")

        # Opcja: przetwarzaj kształty (shapes/drawings)
        self.include_shapes = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Przetwarzaj kształty", variable=self.include_shapes).grid(row=3, column=0, columnspan=3, sticky="w", padx=10)

        tk.Frame(self.root, height=2, bd=1, relief="sunken").grid(row=4, column=0, columnspan=3, sticky="we", pady=10)

        self.btn_convert = tk.Button(self.root, text="Konwertuj PDF", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", width=20, command=self.process_pdf)
        self.btn_convert.grid(row=5, column=0, columnspan=3, pady=5)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pliki PDF", "*.pdf")])
        if file_path:
            self.input_path.set(file_path)
            
            dir_name, file_name = os.path.split(file_path)
            name, ext = os.path.splitext(file_name)
            suggested_output = os.path.join(dir_name, f"{name}_colored{ext}")
            self.output_path.set(suggested_output)

    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Pliki PDF", "*.pdf")])
        if file_path:
            self.output_path.set(file_path)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Wybierz kolor dla PDF")
        if color_code[0]:
            rgb_255 = color_code[0]
            self.chosen_rgb_float = (rgb_255[0]/255.0, rgb_255[1]/255.0, rgb_255[2]/255.0)
            self.color_preview.config(bg=color_code[1])

    def process_pdf(self):
        in_file = self.input_path.get()
        out_file = self.output_path.get()

        if not in_file or not out_file:
            messagebox.showerror("Błąd", "Musisz wybrać plik wejściowy oraz wyjściowy!")
            return

        try:
            self.root.config(cursor="watch")
            self.root.update()

            PDFColor(in_file, out_file, self.chosen_rgb_float, include_shapes=self.include_shapes.get())

            try:
                if sys.platform.startswith("win"):
                    os.startfile(out_file)
                elif sys.platform == "darwin":
                    subprocess.run(["open", out_file], check=False)
                else:
                    subprocess.run(["xdg-open", out_file], check=False)
            except Exception:
                # nie krytyczne — nadal pokażemy komunikat sukcesu
                pass

            self.root.config(cursor="")
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas przetwarzania pliku:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFColorGUI(root)
    root.mainloop()