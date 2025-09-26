import pandas as pd
import requests
from datetime import datetime, timedelta
import random

df = pd.read_csv('OCR_CETRIO_10klinhas.csv', sep=';')

url = "http://127.0.0.1:8000/medicoes"
headers = {
    "Content-Type": "application/json"
}

for index, row in df.iterrows():
    date_str = row['DAT_OCR'].split('/')
    dateObject = datetime(int('20'+date_str[2]), int(date_str[1]), int(date_str[0]), 0, 0)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    dateTimeStr = (dateObject + timedelta(hours=random_hour, minutes=random_minute)).strftime("%Y-%m-%d %H:%M")
    print("Data e hora gerada: ", dateTimeStr)
    payload = {
        "placa": row['NUM_PLACA'],
        "latitude": float(row['COD_LATITUDE']),
        "longitude": float(row['COD_LONGITUDE']),
        "velocidade": float(row['NUM_VELOCIDADE']),
        "timestamp_deteccao": dateTimeStr
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print("POST request successful! - placa: ", payload["placa"])
    else:
        print(f"POST request failed with status code: {response.status_code}")
        print("Response content:", response.text)
