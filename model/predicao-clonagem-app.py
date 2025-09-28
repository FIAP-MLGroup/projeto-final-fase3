import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# Connect to the PostgreSQL database using st.connection
# The name 'postgresql' here refers to the section in your secrets.toml
conn = st.connection("postgresql", type="sql")

def read_medicoes_from_database():
    try:
        query = "SELECT * FROM medicaoradar"
        df = conn.query(query, ttl="10m")  # Cache the result for 10 minutes
        
        return df
    except Exception as e:
        st.error(f"Error querying the database: {e}")
        return pd.DataFrame()
    
def apply_isolation_forest(df):
    if df.empty:
        st.warning("No data available to apply Isolation Forest.")
        return df

    df["hora"] = df["timestamp_deteccao"].dt.hour + df["timestamp_deteccao"].dt.minute/60

    features = df[["latitude","longitude","velocidade","hora"]].values
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    # treinar modelo
    iso = IsolationForest(contamination=0.05, random_state=42)
    df["anomaly_score"] = iso.fit_predict(X)

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

st.title("Detecção de Carros Suspeitos de Clonagem")    
df = read_medicoes_from_database()
df = apply_isolation_forest(df)
anomalias = df[df["anomaly_score"] == -1]

anomalia_rate = (df["anomaly_score"] == -1).mean()
st.metric("Taxa de Anomalias", f"{anomalia_rate:.2%}")


plot_map(anomalias)