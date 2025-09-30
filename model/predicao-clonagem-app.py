import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from geopy.distance import geodesic

# Connect to the PostgreSQL database using st.connection
# The name 'postgresql' here refers to the section in your secrets.toml
conn = st.connection("postgresql", type="sql")

def haversine_km(a, b):
    return geodesic((a[0], a[1]), (b[0], b[1])).km

def load_medicoes_from_database():
    try:
        query = "SELECT * FROM medicaoradar"
        df = conn.query(query, ttl="10m")  # Cache the result for 10 minutes
        
        return df
    except Exception as e:
        st.error(f"Error querying the database: {e}")
        return pd.DataFrame()

def process_pair_features(df):
    pairs = []
    for placa, g in df.sort_values(['placa','timestamp_deteccao']).groupby('placa'):
        rows = g.to_dict('records')
        
        #if len(rows) > 1 and placa == "RKM3695":
        #    print(f"Placa {placa}")
        #    print(g)


        for i in range(len(rows)-1):
            p1, p2 = rows[i], rows[i+1]

            #if placa == "RKM3695":
            #    print(p1)
            #    print(p2)
            
            delta_t_sec = (p2['timestamp_deteccao'] - p1['timestamp_deteccao']).total_seconds()
            if delta_t_sec <= 0: 
                continue
            delta_s = haversine_km((p1['latitude'], p1['longitude']), (p2['latitude'], p2['longitude']))
            velocidade_media = delta_s / (delta_t_sec/3600.0)
            pairs.append({
                'placa': placa,
                'delta_t_sec': delta_t_sec,
                'dist_km': delta_s,
                'v_calc_kmh': velocidade_media,
                'v1': p1['velocidade'],
                'v2': p2['velocidade'],
                'hour': p2['timestamp_deteccao'].hour
            })
    pairs_df = pd.DataFrame(pairs)
    return pairs_df

def apply_isolation_forest(df):
    if df.empty:
        st.warning("No data available to apply Isolation Forest.")
        return df

    features = df[["delta_t_sec", "dist_km", "v_calc_kmh", "v1", "v2"]].values
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    # treinar modelo
    iso = IsolationForest(random_state=42)
    iso.fit(X)
    df["score"] = iso.decision_function(X)
    threshold = -0.1
    df["anomaly"] = (df["score"] < threshold).astype(int)

    return df

def plot_map(anomalias):
    import pydeck as pdk

    format_string = "%Y-%m-%d %H:%M:%S"
    print("Anomalias para plotar: ", anomalias.shape)
    for idx, row in anomalias.iterrows():
        formatted_timestamp = anomalias.loc[idx, 'timestamp_deteccao'].strftime(format_string)
        anomalias.loc[idx, 'formatted_timestamp'] = formatted_timestamp

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
        """
    tooltip = {
        "html": html,
        "style": {"color": "white"}
    }

    # definir a visão inicial do mapa
    midpoint = (-22.9, -43.2)

    view_state = pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=10,
        pitch=0
    )

    # criar o mapa
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

    st.pydeck_chart(r)

st.title("🚦 Radar inteligente - Detecção de clonagem")
df = load_medicoes_from_database()
pairs_df = process_pair_features(df)
anomalias = apply_isolation_forest(pairs_df)

anomalias_to_plot_map = pd.DataFrame()
anomalias_to_plot_expander = pd.DataFrame()

for placa, g in anomalias[anomalias['anomaly'] == 1].groupby('placa'):
    last_anomalia_occur = df[df['placa'] == placa].sort_values('timestamp_deteccao').iloc[-1]
    anomalias_to_plot_map = pd.concat([anomalias_to_plot_map, last_anomalia_occur.to_frame().T], ignore_index=True)
    anomalias_to_plot_expander = pd.concat([
                                                anomalias_to_plot_expander, 
                                                df[df['placa'] == placa].sort_values('timestamp_deteccao')
                                            ]
                                            , ignore_index=True
                                        )

plot_map(anomalias_to_plot_map)

for placa, g in anomalias_to_plot_expander.groupby('placa'):
    with st.expander(f"Placa: {placa} - {g.shape[0]} registros"):
        st.dataframe(g)