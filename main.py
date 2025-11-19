import tkinter as tk
from tkinter import messagebox
import csv
import random
import os

# Mapování úrovní na názvy souborů
LEVEL_FILES = {
    "A1": "cefr_a1_word_list.csv",   # pozor na "cerf"
    "A2": "cefr_a2_word_list.csv",
    "B1": "cefr_b1_word_list.csv",
    "B2": "cefr_b2_word_list.csv",
    "C1": "cefr_c1_word_list.csv",
    "C2": "cefr_c2_word_list.csv",
}


def load_words_for_level(level):
    """Načte slovíčka pro zvolenou úroveň z CSV souboru.

    Vrací seznam dvojic (en, cz).
    """
    filename = LEVEL_FILES.get(level)
    if not filename or not os.path.exists(filename):
        messagebox.showerror("Chyba", f"Soubor pro úroveň {level} nebyl nalezen:\n{filename}")
        return []

    words = []
    with open(filename, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader, None)

        # Zjistíme, který sloupec je anglicky / česky
        eng_index = 0
        cze_index = 1
        if header:
            header_l = [h.lower() for h in header]
            # pokus o detekci
            for i, h in enumerate(header_l):
                if "english" in h or "anglicky" in h:
                    eng_index = i
                if "czech" in h or "česky" in h:
                    cze_index = i

        for row in reader:
            if len(row) <= max(eng_index, cze_index):
                continue
            en = row[eng_index].strip()
            cz = row[cze_index].strip()
            if en and cz:
                words.append((en, cz))
    return words


class VocabApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Procvičování slovní zásoby")
        self.geometry("600x300")

        # Stav aplikace
        self.current_level = None
        self.words = []          # list (en, cz)
        self.direction = "en_to_cz"  # nebo "cz_to_en"
        self.current_index = 0
        self.current_pair = None

        # Různé obrazovky jako frame
        self.level_frame = tk.Frame(self)
        self.direction_frame = tk.Frame(self)
        self.practice_frame = tk.Frame(self)

        self.create_level_screen()
        self.create_direction_screen()
        self.create_practice_screen()

        self.show_frame(self.level_frame)

    # ----------------- Obrazovka 1: výběr úrovně -----------------
    def create_level_screen(self):
        lbl = tk.Label(self.level_frame, text="Vyber úroveň", font=("Arial", 16))
        lbl.pack(pady=20)

        btn_frame = tk.Frame(self.level_frame)
        btn_frame.pack()

        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            btn = tk.Button(btn_frame, text=level, width=8,
                            command=lambda lv=level: self.select_level(lv))
            btn.pack(side=tk.LEFT, padx=5, pady=5)

    def select_level(self, level):
        self.current_level = level
        self.words = load_words_for_level(level)
        if not self.words:
            return
        random.shuffle(self.words)
        self.show_frame(self.direction_frame)

    # ----------------- Obrazovka 2: výběr směru -----------------
    def create_direction_screen(self):
        lbl = tk.Label(self.direction_frame, text="Jakým směrem chceš procvičovat?", font=("Arial", 14))
        lbl.pack(pady=20)

        btn1 = tk.Button(self.direction_frame,
                         text="Angličtina → Čeština",
                         width=25,
                         command=self.set_direction_en_to_cz)
        btn1.pack(pady=5)

        btn2 = tk.Button(self.direction_frame,
                         text="Čeština → Angličtina",
                         width=25,
                         command=self.set_direction_cz_to_en)
        btn2.pack(pady=5)

        back_btn = tk.Button(self.direction_frame, text="Zpět", command=lambda: self.show_frame(self.level_frame))
        back_btn.pack(pady=20)

    def set_direction_en_to_cz(self):
        self.direction = "en_to_cz"
        self.start_practice()

    def set_direction_cz_to_en(self):
        self.direction = "cz_to_en"
        self.start_practice()

    # ----------------- Obrazovka 3: procvičování -----------------
    def create_practice_screen(self):
        self.prompt_label = tk.Label(self.practice_frame, text="", font=("Arial", 18))
        self.prompt_label.pack(pady=20)

        self.entry = tk.Entry(self.practice_frame, font=("Arial", 14), width=40)
        self.entry.pack(pady=5)

        btn_frame = tk.Frame(self.practice_frame)
        btn_frame.pack(pady=10)

        self.check_btn = tk.Button(btn_frame, text="Ověřit", width=10, command=self.check_answer)
        self.check_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(btn_frame, text="Další", width=10, command=self.next_word)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.result_label = tk.Label(self.practice_frame, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

        back_btn = tk.Button(self.practice_frame, text="Zpět na výběr úrovně",
                             command=lambda: self.show_frame(self.level_frame))
        back_btn.pack(pady=10)

    def start_practice(self):
        if not self.words:
            messagebox.showerror("Chyba", "Nebyla načtena žádná slovíčka.")
            return
        self.current_index = 0
        random.shuffle(self.words)
        self.next_word()
        self.show_frame(self.practice_frame)

    def next_word(self):
        if not self.words:
            return

        if self.current_index >= len(self.words):
            # Pokud dojdeme na konec, zamícháme a začneme znovu
            random.shuffle(self.words)
            self.current_index = 0

        self.current_pair = self.words[self.current_index]
        self.current_index += 1

        en, cz = self.current_pair
        if self.direction == "en_to_cz":
            self.prompt_label.config(text=en)
        else:
            self.prompt_label.config(text=cz)

        # Vyčistit vstup a výsledek
        self.entry.delete(0, tk.END)
        self.entry.config(bg="white")
        self.result_label.config(text="")

    def check_answer(self):
        if not self.current_pair:
            return

        user_answer = self.entry.get().strip().lower()
        en, cz = self.current_pair

        # Dle směru určujeme správné odpovědi
        if self.direction == "en_to_cz":
            correct_field = cz
        else:
            correct_field = en

        # Rozdělení na více možných variant (oddělené čárkou nebo lomítkem)
        variants = []
        for part in correct_field.replace("/", ",").split(","):
            v = part.strip().lower()
            if v:
                variants.append(v)

        if user_answer in variants:
            # Správně
            self.entry.config(bg="#c8e6c9")  # světle zelená
            self.result_label.config(text="Správně!")
        else:
            # Špatně
            self.entry.config(bg="#ffcdd2")  # světle červená
            self.result_label.config(
                text=f"Nesprávně. Správná odpověď: {correct_field}"
            )

    # ----------------- Pomocné -----------------
    def show_frame(self, frame):
        """Zobrazí daný frame a ostatní schová."""
        for f in (self.level_frame, self.direction_frame, self.practice_frame):
            f.pack_forget()
        frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = VocabApp()
    app.mainloop()
