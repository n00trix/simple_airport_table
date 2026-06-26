import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import datetime
import requests

TIME_RANGES = {
    "00:00-02:00": ("00:00", "02:00"),
    "02:00-04:00": ("02:00", "04:00"),
    "04:00-06:00": ("04:00", "06:00"),
    "06:00-08:00": ("06:00", "08:00"),
    "08:00-10:00": ("08:00", "10:00"),
    "10:00-12:00": ("10:00", "12:00"),
    "12:00-14:00": ("12:00", "14:00"),
    "14:00-16:00": ("14:00", "16:00"),
    "16:00-18:00": ("16:00", "18:00"),
    "18:00-20:00": ("18:00", "20:00"),
    "20:00-22:00": ("20:00", "22:00"),
    "22:00-00:00": ("22:00", "00:00"),
}

AIRPORTS = {
    "Домодедово (DME)": "DME",
    "Внуково (VKO)": "VKO",
    "Шереметьево (SVO)": "SVO",
    "Пулково (LED)": "LED"
}

DORA = ["Прилеты", "Вылеты"]


def fetch_departures(d, date_str, time_f, time_t):
    url = f"https://timetable.kupibilet.ru/api/v1/schedule/departure/{d}"
    params = {
        "date": date_str,
        "lang": "ru",
        "departure_time_from": time_f,
        "departure_time_to": time_t,
    }
    headers = {"Accept": "application/json"}

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()

    data = r.json()
    items = data if isinstance(data, list) else []

    rows = []
    for item in items:
        marketing = item.get("marketing_carrier")
        number = item.get("number")

        if marketing and number:
            flight = f"{marketing} {number}"
        else:
            flight = number or ""

        last_status = item.get("last_status")
        if last_status == "scheduled":
            a = "по расписанию"
        elif last_status == "unknown":
            a = "неизвестно"
        elif last_status == "landed":
            a = "приземлился"
        elif last_status == "active":
            a = "активный"
        else:
            a = last_status or ""

        rows.append({
            "Время": item.get("departure_estimated_time") or item.get("departure_time"),
            "Рейс": flight,
            "Терминал": item.get("departure_terminal"),
            "Направление": item.get("arrival_city_name"),
            "Статус": a,
            "Ворота": item.get("departure_gate"),
        })

    return pd.DataFrame(rows)


def fetch_arrivals(d, date_str, time_f, time_t):
    url = f"https://timetable.kupibilet.ru/api/v1/schedule/arrival/{d}"
    params = {
        "date": date_str,
        "lang": "ru",
        "departure_time_from": time_f,
        "departure_time_to": time_t,
    }
    headers = {"Accept": "application/json"}

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()

    data = r.json()
    items = data if isinstance(data, list) else []

    rows = []
    for item in items:
        operating = item.get("operating_carrier")
        number = item.get("number")

        if operating and number:
            flight = f"{operating} {number}"
        else:
            flight = number or ""

        last_status = item.get("last_status")
        if last_status == "scheduled":
            a = "по расписанию"
        elif last_status == "unknown":
            a = "неизвестно"
        elif last_status == "landed":
            a = "приземлился"
        elif last_status == "active":
            a = "активный"
        elif last_status == "-":
            a = "-"
        else:
            a = last_status or ""

        rows.append({
            "Время": item.get("arrival_estimated_time") or item.get("arrival_time"),
            "Рейс": flight,
            "Терминал": item.get("arrival_terminal"),
            "Направление": item.get("departure_city_name"),
            "Статус": a,
            "Ворота": item.get("arrival_gate"),
        })

    return pd.DataFrame(rows)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Расписание аэропортов (Прилеты/Вылеты)")
        self.geometry("1050x600")

        frm = tk.Frame(self)
        frm.pack(fill="x", padx=10, pady=10)

        tk.Label(frm, text="Тип:").grid(row=0, column=0, sticky="w")
        self.dora_choice = ttk.Combobox(frm, values=DORA, state="readonly", width=22)
        self.dora_choice.current(0)
        self.dora_choice.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frm, text="Временной промежуток:").grid(row=0, column=2, sticky="w")
        self.time_choice = ttk.Combobox(frm, values=list(TIME_RANGES.keys()), state="readonly", width=22)
        self.time_choice.current(0)
        self.time_choice.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        tk.Label(frm, text="Аэропорт:").grid(row=1, column=0, sticky="w")
        self.air_choice = ttk.Combobox(frm, values=list(AIRPORTS.keys()), state="readonly", width=25)
        self.air_choice.current(0)
        self.air_choice.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frm, text="Дата (например 2026-06-24 или 'нынешнее'):").grid(row=1, column=2, sticky="w")
        self.date_entry = tk.Entry(frm, width=20)
        self.date_entry.insert(0, "нынешнее")
        self.date_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        self.btn = tk.Button(frm, text="Получить", command=self.on_get)
        self.btn.grid(row=2, column=3, padx=10, pady=5, sticky="e")

        self.status_var = tk.StringVar(value="Готово.")
        tk.Label(frm, textvariable=self.status_var, fg="blue").grid(row=2, column=1, padx=10, pady=5, sticky="w")

        cols = ["Время", "Рейс", "Терминал", "Направление", "Статус", "Ворота"]

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=130, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<MouseWheel>", self._on_mousewheel)
        self.tree.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _on_mousewheel(self, event):
        # Windows: event.delta кратен 120
        self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        self.tree.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def on_get(self):
        self.status_var.set("Загрузка...")
        self.update_idletasks()

        try:
            dora = self.dora_choice.get()
            time_range_key = self.time_choice.get()
            time_f, time_t = TIME_RANGES[time_range_key]

            airport_key = self.air_choice.get()
            d = AIRPORTS[airport_key]

            date_in = self.date_entry.get().strip()
            if date_in == "нынешнее":
                date = datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date = date_in

            if dora == "Прилеты":
                df = fetch_arrivals(d=d, date_str=date, time_f=time_f, time_t=time_t)
            else:
                df = fetch_departures(d=d, date_str=date, time_f=time_f, time_t=time_t)

            self.clear_tree()
            if df.empty:
                self.status_var.set("Нет данных.")
                return

            for _, row in df.iterrows():
                values = [row.get(col, "") for col in ["Время", "Рейс", "Терминал", "Направление", "Статус", "Ворота"]]
                self.tree.insert("", "end", values=values)

            self.status_var.set(f"Готово. Строк: {len(df)}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка запроса", str(e))
            self.status_var.set("Ошибка.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_var.set("Ошибка.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
