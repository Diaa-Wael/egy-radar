import streamlit as st
import requests
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(
    page_title="EGY-RADAR | Tactical Weather", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Global Reset */
    [data-testid="stHeader"], footer {display: none !important;}
    
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }
    
    .stAppViewMain { padding-top: 0 !important; }

    /* FULLSCREEN IFRAME FIX */
    iframe, .element-container iframe, [data-testid="stIFrame"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 0 !important;
        border: none !important;
    }

    /* STATIC SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #080808 !important;
        border-right: 2px solid #1E293B;
        z-index: 99999 !important;
    }

    /* NEON-REACTIVE METRIC BOXES */
    div[data-testid="stMetric"] {
        background: #111827 !important;
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 6px;
        padding: 10px;
        transition: all 0.3s ease-in-out; /* Smooth fade for the glow */
        cursor: pointer;
    }

    /* THE HOVER EFFECT: Blue Glow */
    div[data-testid="stMetric"]:hover {
        border: 1px solid #38BDF8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4), inset 0 0 10px rgba(56, 189, 248, 0.2);
        transform: translateY(-2px); /* Subtle lift effect */
    }

    /* HIGH-VISIBILITY NUMBERS */
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold !important;
        font-size: 1.4rem !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* GLOW FOR INTERACTIVE INPUTS (Selectboxes & Sliders) */
    .stSelectbox div[data-baseweb="select"], .stSlider {
        transition: all 0.3s ease-in-out;
    }
    .stSelectbox:hover div[data-baseweb="select"] {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }

    .stApp { background-color: #000; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_tactical_data(lat, lon):
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,dew_point_2m,surface_pressure,precipitation&hourly=temperature_2m,precipitation_probability&forecast_days=1"
        aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,pm10,pm2_5"
        
        w_res, aq_res = requests.get(w_url).json(), requests.get(aq_url).json()
        curr_h = datetime.now().hour
        
        return {
            "current": {
                "temp": w_res['current']['temperature_2m'],
                "hum": w_res['current']['relative_humidity_2m'],
                "dew": w_res['current']['dew_point_2m'],
                "press": w_res['current']['surface_pressure'],
                "rain_prob": w_res['hourly']['precipitation_probability'][curr_h],
                "aqi": aq_res['current']['european_aqi'],
                "pm25": aq_res['current']['pm2_5'], "pm10": aq_res['current']['pm10']
            },
            "hourly": {"temps": w_res['hourly']['temperature_2m'], "times": [f"{i}:00" for i in range(24)]}
        }
    except: return None

SECTORS = {
    "Cairo Hub": {"lat": 30.04, "lon": 31.23, "info": "Primary Operational Zone"},
    "Alexandria Port": {"lat": 31.20, "lon": 29.91, "info": "Maritime Climate Sector"},
    "Sharm Terminal": {"lat": 27.91, "lon": 34.33, "info": "Red Sea Observation"},
    "Aswan Deep South": {"lat": 24.08, "lon": 32.89, "info": "High Aridity Zone"},
    "Siwa Frontier": {"lat": 29.20, "lon": 25.51, "info": "Western Desert Basin"}
}
LAYERS = {"Wind Velocity": "wind", "Precipitation": "rain", "Heat Index": "temp", "Dust/Aerosol": "dust"}

with st.sidebar:
    st.markdown("<h2 style='color:#38BDF8; letter-spacing:-1px; margin:0;'>EGY-RADAR</h2><p style='color:#475569; font-size:0.7rem; margin-bottom:1rem;'>EGYPTIAN WEATHER RADAR</p>", unsafe_allow_html=True)
    
    sector = st.selectbox("ACTIVE SECTOR", list(SECTORS.keys()))
    overlay = st.selectbox("VISUALIZATION", list(LAYERS.keys()))
    zoom = st.slider("RADAR ZOOM", 5, 13, 10)
    
    data = fetch_tactical_data(SECTORS[sector]['lat'], SECTORS[sector]['lon'])
    
    if data:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("TEMP", f"{data['current']['temp']}°")
        c2.metric("DEW PT", f"{data['current']['dew']}°")
        c3.metric("HUM", f"{data['current']['hum']}%")
        
        st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
        
        c4, c5, c6 = st.columns(3)
        c4.metric("BARO", f"{int(data['current']['press'])}")
        c5.metric("RAIN", f"{data['current']['rain_prob']}%")
        c6.metric("AQI", f"{data['current']['aqi']}")

        st.markdown("---")
        st.markdown("### 🧪 POLLUTANTS")
        c7, c8 = st.columns(2)
        c7.metric("PM2.5", f"{data['current']['pm25']}")
        c8.metric("PM10", f"{data['current']['pm10']}")

        fig = go.Figure(go.Scatter(x=data['hourly']['times'], y=data['hourly']['temps'], fill='tozeroy', line=dict(color='#38BDF8', width=2)))
        fig.update_layout(height=100, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')} EET")

windy_url = f"https://embed.windy.com/embed2.html?lat={SECTORS[sector]['lat']}&lon={SECTORS[sector]['lon']}&zoom={zoom}&overlay={LAYERS[overlay]}&product=ecmwf&marker=true"

components.html(f"""
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background: #000; }}
        iframe {{ width: 100vw; height: 100vh; border: none; filter: saturate(1.2) brightness(0.9); }}
    </style>
    <iframe src="{windy_url}" allowfullscreen></iframe>
    """, height=2000)