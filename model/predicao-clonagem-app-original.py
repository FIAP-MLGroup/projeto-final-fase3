import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import streamlit as st
import pydeck as pdk

# fixar semente
np.random.seed(42)
random.seed(42)

# placas simuladas
placas_normais = [f"ABC{n:03d}" for n in range(50)]
#placas_suspeitas = ["CLONE1", "CLONE2", "COMBOIO1", "COMBOIO2"]
placas_suspeitas = ["CLONE1", "CLONE2"]

# pontos do RJ (lat/lon aproximados)
pontos_normais = [(-22.90, -43.20), (-22.95, -43.25), (-22.85, -43.30)]  # Centro/Zona Sul
pontos_risco = [(-22.87, -43.28), (-22.99, -43.25)]  # áreas críticas simuladas

# gerar dataset
registros = []
base_time = datetime(2023, 7, 23, 9, 0, 0)

# tráfego normal
for placa in placas_normais:
    for i in range(5):
        lat, lon = random.choice(pontos_normais)
        registros.append({
            "placa": placa,
            "latitude": lat + np.random.normal(0, 0.002),
            "longitude": lon + np.random.normal(0, 0.002),
            "velocidade": np.random.randint(30, 60),
            "timestamp": base_time + timedelta(minutes=random.randint(0, 120))
        })

# veículos suspeitos
# CLONE1: aparece em pontos muito distantes em intervalo curto
registros.append({"placa":"CLONE1","latitude":-22.90,"longitude":-43.20,"velocidade":40,"timestamp":base_time+timedelta(minutes=10)})
registros.append({"placa":"CLONE1","latitude":-22.99,"longitude":-43.25,"velocidade":50,"timestamp":base_time+timedelta(minutes=15)})

#23/07/23;"QNX4H77";43;"-22.9911111000";"-43.5936111111";"ESTRADA DO MATO ALTO PROXIMO AO Nº 959 - SENTIDO BARRA - FX 1";"09:13:25"
#23/07/23;"QNX4H77";60;"-22.9043993037786";"-43.28823403214526";"DIAS DA CRUZ - MEIER";"09:30:44"

registros.append({"placa":"QNX4H77","latitude":-22.99,"longitude":-43.59,"velocidade":43,"timestamp":base_time+timedelta(minutes=13)})
registros.append({"placa":"QNX4H77","latitude":-22.99,"longitude":-43.59,"velocidade":43,"timestamp":base_time+timedelta(minutes=30)})

# CLONE2: só aparece em área de risco
for i in range(3):
    lat, lon = random.choice(pontos_risco)
    registros.append({"placa":"CLONE2","latitude":lat,"longitude":lon,"velocidade":45,"timestamp":base_time+timedelta(minutes=20*i)})

# COMBOIO1 e COMBOIO2: passam juntos em vários pontos
#for i in range(3):
#    lat, lon = random.choice(pontos_normais + pontos_risco)
#    t = base_time + timedelta(minutes=5*i)
#    for placa in ["COMBOIO1","COMBOIO2"]:
#        registros.append({
#            "placa": placa,
#            "latitude": lat + np.random.normal(0, 0.0005),
#            "longitude": lon + np.random.normal(0, 0.0005),
#            "velocidade": np.random.randint(60, 80),
#            "timestamp": t
#        })

df = pd.DataFrame(registros)
df["hora"] = df["timestamp"].dt.hour + df["timestamp"].dt.minute/60

features = df[["latitude","longitude","velocidade","hora"]].values
scaler = StandardScaler()
X = scaler.fit_transform(features)

# treinar modelo
iso = IsolationForest(contamination=0.05, random_state=42)
df["anomaly_score"] = iso.fit_predict(X)

# -1 = anômalo, 1 = normal
anomalias = df[df["anomaly_score"] == -1]
print("🔎 Veículos suspeitos detectados:")
print(anomalias[["placa","latitude","longitude","velocidade","timestamp"]])

#anomalias['formatted_timestamp'] = anomalias['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
format_string = "%Y-%m-%d %H:%M:%S"
for idx, row in anomalias.iterrows():
    formatted_timestamp = anomalias.loc[idx, 'timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    anomalias.loc[idx, 'formatted_timestamp'] = formatted_timestamp
    other_ocurrences = df.loc[df['placa'] == anomalias.loc[idx, 'placa']]['timestamp'].tolist()
    other_ocurrences = [dt.strftime(format_string) for dt in other_ocurrences]
    anomalias.loc[idx, 'other_ocurrences'] = ", ".join(other_ocurrences)

st.title("Detecção de Carros Suspeitos de Clonagem")

# camada de pontos com tooltip
layer = pdk.Layer(
    "ScatterplotLayer",
    data=anomalias,
    get_position='[longitude, latitude]',
    get_color='[200, 30, 0, 160]',
    get_radius=100,
    pickable=True
)

# tooltip configurável
html = """
        <b>Placa:</b> {placa}
        <br/>
        <b>Velocidade:</b> {velocidade} km/h
        <br/>
        <b>Hora:</b> {formatted_timestamp}
        <br/>
        <b>Outras ocorrências:</b> {other_ocurrences}
    """
tooltip = {
    "html": html,
    #"html": "<b>Placa:</b> {placa} <br/> <b>Velocidade:</b> {velocidade} km/h <br/> <b>Hora:</b> {formatted_timestamp}",
    "style": {"color": "white"}
}

# mapa
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=-22.90,
        longitude=-43.17,
        zoom=11,
        pitch=0
    ),
    tooltip=tooltip
)

st.pydeck_chart(deck)