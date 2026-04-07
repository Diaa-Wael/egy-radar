import streamlit as st
import requests
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(
    page_title="Egypt Weather Monitor", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* 1. HIDE TOP BAR & FOOTER (STAYING DISCRETE) */
    header, footer, .stDeployButton, [data-testid="stDecoration"] {display: none !important;}

    /* 2. CLOUD COMPATIBLE LOCK (Prevents the 'Disappearing Act') */
    /* We target only the main scroll containers, not the whole App */
    [data-testid="stMainViewContainer"], [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }

    /* 3. EYE-COMFY THEME */
    .stApp { 
        background-color: #121212; 
        color: #E0E0E0; 
        font-family: 'Inter', sans-serif;
    }

    /* 4. SIDEBAR FIX: Keep content visible and static */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 2rem !important;
    }
    
    /* 5. MAIN PAGE: Edge-to-Edge Map */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
    }

    /* 6. METRIC BOXES: High-Contrast */
    div[data-testid="stMetric"] { 
        background-color: #1E1E1E; 
        border: 1px solid #333; 
        padding: 15px; 
        border-radius: 10px;
        margin-bottom: 8px;
    }
    div[data-testid="stMetricLabel"] { color: #AAAAAA !important; font-size: 0.8rem !important; }
    div[data-testid="stMetricValue"] { color: #38BDF8 !important; font-size: 1.4rem !important; }
    
    /* Progress Bar */
    div[st-component="stProgress"] > div > div > div > div { background-color: #38BDF8 !important; }
    </style>
    """, unsafe_allow_html=True)

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
    url = f"https://api.open-meteo.com/v1/forecast?latitude={c['lat']}&longitude={c['lon']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&hourly=precipitation_probability"
    try:
        res = requests.get(url).json()
        curr_h = datetime.now().hour
        return {
            "temp": res['current']['temperature_2m'],
            "hum": res['current']['relative_humidity_2m'],
            "wind": res['current']['wind_speed_10m'],
            "rain": res['hourly']['precipitation_probability'][curr_h]
        }
    except:
        return {"temp": "--", "hum": "--", "wind": "--", "rain": 0}

weather = fetch_weather(st.session_state.city)
coords = SECTORS[st.session_state.city]

with st.sidebar:
    st.markdown("<h2 style='margin-top:0;'>Weather Hub</h2>", unsafe_allow_html=True)
    
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
    st.progress(weather['rain'] / 100)
    st.markdown("---")
    st.caption(f"Sync: {datetime.now().strftime('%H:%M')} EET")

windy_url = f"https://embed.windy.com/embed2.html?lat={coords['lat']}&lon={coords['lon']}&zoom={coords['zoom']}&overlay=wind&product=ecmwf&marker=true"

components.html(f"""
    <iframe src="{windy_url}" 
    width="100%" 
    height="100%" 
    frameborder="0" 
    style="position: fixed; top: 0; left: 0; width: 100%; height: 100vh; border: none;"></iframe>
    """, height=1200) # Large height prevents 'thin map' on high-res screens
