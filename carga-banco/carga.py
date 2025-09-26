import pandas as pd
import requests
from datetime import datetime, timedelta
import random

#df = pd.read_csv('OCR_CETRIO_10klinhas.csv', sep=';', nrows=10)
df = pd.read_csv('OCR_CETRIO_10klinhas.csv', sep=';')

url = "http://127.0.0.1:8000/medicoes"
headers = {
    "Content-Type": "application/json"
}

# Popula o banco de dados com os dados do CSV
for index, row in df.iterrows():
    date_str = row['DAT_OCR'].split('/')
    date_object = datetime(int('20'+date_str[2]), int(date_str[1]), int(date_str[0]), 0, 0)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    dateTimeStr = (date_object + timedelta(hours=random_hour, minutes=random_minute)).strftime("%Y-%m-%d %H:%M")
    
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
        df.loc[index, 'TIMESTAMP_DETECCAO'] = dateTimeStr # Adiciona a nova coluna ao DataFrame
    else:
        print(f"POST request failed with status code: {response.status_code}")
        print("Response content:", response.text)

#print("Dados do CSV com timestamps atualizados:")
#print(df)

# áreas críticas simuladas
pontos_risco = [
    (-22.87, -43.28), #Inhaúma
    (-22.99, -43.25), #Rocinha
    (-22.852946889130063, -43.240993919652176), #Complexo da Maré
    (-22.88369132487631, -43.24808490059974), #Manguinhos
    (-22.946656340196, -43.37022098632127) #Cidade de Deus     
]

for i in range(50):
    # Gerando dados de clonagem de veículos se baseando em dados reais do CSV
    random_num = random.randint(1, len(df))
    random_row = df.iloc[random_num]
    random_timestamp_deteccao = datetime.strptime(random_row['TIMESTAMP_DETECCAO'], "%Y-%m-%d %H:%M")

    lat, lon = random.choice(pontos_risco)
    payload = {
        "placa": random_row['NUM_PLACA'],
        "latitude": lat,
        "longitude": lon,
        "velocidade": random.randint(30, 100),
        "timestamp_deteccao": (random_timestamp_deteccao + timedelta(minutes=random.randint(1,15))).strftime("%Y-%m-%d %H:%M")
    }

    # print("Payload gerado: ", payload)

    response = requests.post(url, json=payload)
        
    if response.status_code == 201:
        print("Placa clonada com sucesso: ", payload["placa"])
    else:
        print("Erro na clonagem da placa.")
        print(f"POST request failed with status code: {response.status_code}")
        print("Response content:", response.text)