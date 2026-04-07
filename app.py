import streamlit as st
import requests
import streamlit.components.v1 as components
from datetime import datetime

# --- 1. SETTINGS & CLOUD CSS ---
st.set_page_config(page_title="Egypt Weather Monitor", layout="wide")

st.markdown("""
    <style>
    header, footer, .stDeployButton {display: none !important;}
    [data-testid="stMainViewContainer"] { overflow: hidden !important; }
    .stApp { background-color: #121212; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    div[data-testid="stMetric"] { 
        background-color: #1E1E1E; border: 1px solid #333; 
        padding: 15px; border-radius: 10px; margin-bottom: 8px;
    }
    div[data-testid="stMetricValue"] { color: #38BDF8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (Cloud Optimized) ---
SECTORS = {
    "Cairo": {"lat": 30.04, "lon": 31.23, "zoom": 10},
    "Alexandria": {"lat": 31.20, "lon": 29.91, "zoom": 10},
    "Marsa Matrouh": {"lat": 31.35, "lon": 27.24, "zoom": 10},
    "Sharm El Sheikh": {"lat": 27.91, "lon": 34.33, "zoom": 11},
    "Central Sinai": {"lat": 28.55, "lon": 33.95, "zoom": 9},
    "Suez": {"lat": 29.96, "lon": 32.54, "zoom": 10},
    "Port Said": {"lat": 31.26, "lon": 32.30, "zoom": 10},
    "Luxor": {"lat": 25.68, "lon": 32.63, "zoom": 10},
    "Aswan": {"lat": 24.08, "lon": 32.89, "zoom": 10},
    "Hurghada": {"lat": 27.25, "lon": 33.81, "zoom": 10}
}

if 'city' not in st.session_state:
    st.session_state.city = "Cairo"

@st.cache_data(ttl=300)
def fetch_weather(city):
    c = SECTORS[city]
    # Forced HTTPS for Cloud Security
    url = f"https://api.open-meteo.com/v1/forecast?latitude={c['lat']}&longitude={c['lon']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&hourly=precipitation_probability"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Check if the request was successful
        data = response.json()
        curr_h = datetime.now().hour
        return {
            "temp": data['current']['temperature_2m'],
            "hum": data['current']['relative_humidity_2m'],
            "wind": data['current']['wind_speed_10m'],
            "rain": data['hourly']['precipitation_probability'][curr_h]
        }
    except Exception as e:
        # This will show up in your Streamlit Cloud logs
        print(f"Error fetching data for {city}: {e}")
        return {"temp": "Error", "hum": "Error", "wind": "Error", "rain": 0}

weather = fetch_weather(st.session_state.city)
coords = SECTORS[st.session_state.city]

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("Weather Hub")
    selected = st.selectbox("Location", options=list(SECTORS.keys()), 
                            index=list(SECTORS.keys()).index(st.session_state.city))
    if selected != st.session_state.city:
        st.session_state.city = selected
        st.rerun()

    st.markdown("---")
    st.metric("Temperature", f"{weather['temp']} °C")
    st.metric("Wind Speed", f"{weather['wind']} km/h")
    st.metric("Humidity", f"{weather['hum']} %")
    st.metric("Rain Chance", f"{weather['rain']} %")
    st.progress(int(weather['rain']) / 100 if isinstance(weather['rain'], int) else 0)
    st.caption(f"Sync: {datetime.now().strftime('%H:%M')} EET")

# --- 4. MAP ---
windy_url = f"https://embed.windy.com/embed2.html?lat={coords['lat']}&lon={coords['lon']}&zoom={coords['zoom']}&overlay=wind&product=ecmwf&marker=true"
components.html(f'<iframe src="{windy_url}" width="100%" height="100vh" frameborder="0" style="position: fixed; top: 0; left: 0; width: 100%; height: 100vh; border: none;"></iframe>', height=1000)
