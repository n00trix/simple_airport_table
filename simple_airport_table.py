import pandas as pd
import datetime
import requests
d = ""
print("Выбери временной промежуток: 1)00:00-02:00, 2)02:00-04:00, 3)04:00-06:00, 4)06:00-08:00, 5)08:00-10:00, 6)10:00-12:00, 7)12:00-14:00, 8)14:00-16:00, 9)16:00-18:00, 10)18:00-20:00, 11)20:00-22:00, 12)22:00-00:00 ")
a = int(input())
print("Введите дату(к примеру 2026-06-24) или нынешнее")
date = input()
if date == "нынешнее":
    date = datetime.datetime.now()
if a == 1:
    time_f = "00:00"
    time_t = "02:00"
elif a == 2:
     time_f = "02:00"
     time_t = "04:00"
if a == 3:
    time_f = "04:00"
    time_t = "06:00"
elif a == 4:
     time_f = "06:00"
     time_t = "08:00"
if a == 5:
    time_f = "08:00"
    time_t = "10:00"
elif a == 6:
     time_f = "10:00"
     time_t = "12:00"
if a == 7:
    time_f = "12:00"
    time_t = "14:00"
elif a == 8:
     time_f = "14:00"
     time_t = "16:00"
if a == 9:
    time_f = "16:00"
    time_t = "18:00"
elif a == 10:
     time_f = "18:00"
     time_t = "20:00"
if a == 11:
    time_f = "20:00"
    time_t = "22:00"
elif a == 12:
     time_f = "22:00"
     time_t = "00:00"
print("Выбери аэропорт: 1 Домодедово(DME), 2 Внуково(VKO), 3 Шереметьево(SVO) ")
c = int(input())
if c == 1:
    d = "DME"
elif c == 2:
    d = "VKO"
elif c == 3:
    d = "SVO"
url = f"https://timetable.kupibilet.ru/api/v1/schedule/departure/{d}"
params = {
    "date": date,
    "lang": "ru",
    "departure_time_from": time_f,
    "departure_time_to": time_t,
}
headers = {"Accept": "application/json"}

r = requests.get(url, params=params, headers=headers, timeout=10)
r.raise_for_status()

data = r.json()
rows = []
items = data if isinstance(data, list) else []

for item in items:
    marketing = item.get("marketing_carrier")
    number = item.get("number")

    if marketing and number:
        flight = f"{marketing} {number}"
    else:
        flight = number or ""
    rows.append({
        "Время": item.get("departure_estimated_time") or item.get("departure_time"),
        "Рейс": flight,
        "Терминал": item.get("departure_terminal"),
        "Направление": item.get("arrival_city_name"),
        "Статус": item.get("last_status"),
        "Ворота": item.get("departure_gate"),
    })


df = pd.DataFrame(rows)
print(df)
