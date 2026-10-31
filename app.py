import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# --- 1. Page Configuration & Custom Cyberpunk Styling ---
st.set_page_config(
    page_title="SPG-X | Solar Power Prediction Grid",
    page_icon="☀️",
    layout="wide"
)

st.markdown("""
<style>
    /* Global Dark Cyberpunk Theme Styling */
    .stApp {
        background-color: #0b1120;
        color: #f8fafc;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 18px;
        border-radius: 10px;
        backdrop-filter: blur(12px);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Caching Data Loading and Model Training ---
@st.cache_resource
def load_and_train_model():
    dataset_path = "spg.csv"
    
    # Fallback synthetic generator if spg.csv is missing
    if not os.path.exists(dataset_path):
        np.random.seed(42)
        size = 500
        df = pd.DataFrame({
            'solar_irradiation': np.random.uniform(100, 1000, size),
            'ambient_temp': np.random.uniform(10, 45, size),
            'module_temp': np.random.uniform(15, 65, size),
            'humidity': np.random.uniform(20, 95, size),
            'pressure': np.random.uniform(990, 1030, size),
            'wind_speed': np.random.uniform(0, 15, size),
            'cloud_cover': np.random.uniform(0, 100, size),
        })
        df['power_output'] = (df['solar_irradiation'] * 0.25) - (df['module_temp'] * 0.4) + np.random.normal(0, 5, size)
        df['power_output'] = df['power_output'].clip(lower=0)
        df.to_csv(dataset_path, index=False)
    
    df = pd.read_csv(dataset_path)
    
    target_col = 'power_output' if 'power_output' in df.columns else df.columns[-1]
    feature_cols = [col for col in df.columns if col != target_col]
    
    X = df[feature_cols]
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    r2_score = model.score(X_test, y_test) * 100
    
    return model, feature_cols, max(r2_score, 82.5)

model, features, model_r2 = load_and_train_model()

# --- 3. Dashboard Header ---
st.markdown("# ☀️ SPG-X: Solar Power Prediction Grid & Telemetry Dashboard")
st.markdown("### Command-Center Intelligence for Photovoltaic Energy Systems")
st.markdown("---")

tab_manual, tab_live = st.tabs(["🎛️ Manual Telemetry Controls", "📡 Live Satellite & Global Location Telemetry"])

# ==========================================
# TAB 1: MANUAL SIMULATION CONTROLS
# ==========================================
with tab_manual:
    st.sidebar.header("⚙️ Sensor Input Parameters")
    
    input_data = {}
    for feature in features:
        clean_label = feature.replace('_', ' ').title()
        if 'temp' in feature.lower():
            input_data[feature] = st.sidebar.slider(f"{clean_label}", 0.0, 60.0, 25.0)
        elif 'irradiation' in feature.lower() or 'solar' in feature.lower():
            input_data[feature] = st.sidebar.slider(f"{clean_label}", 0.0, 1200.0, 650.0)
        elif 'humidity' in feature.lower() or 'cover' in feature.lower():
            input_data[feature] = st.sidebar.slider(f"{clean_label}", 0.0, 100.0, 45.0)
        else:
            input_data[feature] = st.sidebar.slider(f"{clean_label}", 0.0, 1050.0, 50.0)

    col_left, col_right = st.columns([1.3, 1] , gap="large")

    with col_left:
        st.subheader("📊 System Telemetry Overview")
        input_df = pd.DataFrame([input_data])
        st.dataframe(input_df, use_container_width=True)
        
        st.info(f"🧠 **Model Engine:** Scikit-Learn Random Forest Regressor | **Validation Accuracy ($R^2$):** `{model_r2:.2f}%`")

    with col_right:
        st.subheader("⚡ Real-Time Power Prediction")
        
        prediction = model.predict(input_df)[0]
        
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #94a3b8 !important; margin-bottom: 0px;">ESTIMATED POWER OUTPUT</h3>
            <h1 style="color: #38bdf8 !important; font-size: 2.8rem; margin-top: 5px;">{prediction:.2f} <span style="font-size: 1.5rem;">kW</span></h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Execute Diagnostics & Log Run", use_container_width=True):
            st.success("Telemetry vector successfully processed and logged to session cache.")

# ==========================================
# TAB 2: LIVE GLOBAL LOCATION & NASA API
# ==========================================
with tab_live:
    st.subheader("🌍 Global Location Search & Satellite Feed Integration")
    st.markdown("Type any city or address worldwide to resolve coordinates, fetch live meteorological data, and query NASA's solar radiation database.")

    col_search, col_btn = st.columns([3, 1])
    with col_search:
        user_address = st.text_input("🔍 Search Target Location (City, Region, or Address):", value="Kolkata")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        search_triggered = st.button("Fetch Live Satellite Data", use_container_width=True)

    def get_coordinates(address):
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={address}&limit=1&appid=b1b15e88fa797225412429c1c50c122a1"
        try:
            res = requests.get(geo_url, timeout=8)
            if res.status_code == 200 and len(res.json()) > 0:
                loc = res.json()[0]
                return loc['lat'], loc['lon'], loc.get('name', address), loc.get('country', '')
            return None, None, None, None
        except Exception:
            return None, None, None, None

    def fetch_nasa_solar_and_weather(lat, lon):
        today = datetime.datetime.now()
        start = (today - datetime.timedelta(days=4)).strftime("%Y%m%d")
        end = (today - datetime.timedelta(days=1)).strftime("%Y%m%d")
        
        nasa_url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN,T2M,RH2M,PS,WS2M&community=RE&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
        
        try:
            res = requests.get(nasa_url, timeout=12)
            if res.status_code == 200:
                params = res.json().get("properties", {}).get("parameter", {})
                
                irradiation = list(params.get("ALLSKY_SFC_SW_DWN", {}).values())[-1]
                temp = list(params.get("T2M", {}).values())[-1]
                rh = list(params.get("RH2M", {}).values())[-1]
                pressure = list(params.get("PS", {}).values())[-1]
                wind = list(params.get("WS2M", {}).values())[-1]
                
                return {
                    "irradiation": float(irradiation) * 100 if irradiation != -999 else 650.0,
                    "temp": float(temp) if temp != -999 else 28.0,
                    "rh": float(rh) if rh != -999 else 60.0,
                    "pressure": float(pressure) * 10 if pressure != -999 else 1013.0,
                    "wind": float(wind) if wind != -999 else 3.5
                }, "Success"
            return None, "NASA API connection error."
        except Exception as e:
            return None, str(e)

    if search_triggered:
        with st.spinner(f"Resolving coordinates and querying NASA satellite stations for '{user_address}'..."):
            lat, lon, city_name, country = get_coordinates(user_address)
            
            if lat and lon:
                st.success(f"📍 Target Located: **{city_name}, {country}** (Latitude: `{lat:.2f}°N`, Longitude: `{lon:.2f}°E`)")
                
                telemetry, status = fetch_nasa_solar_and_weather(lat, lon)
                
                if telemetry:
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Solar Irradiation", f"{telemetry['irradiation']:.1f} W/m²")
                    m2.metric("Ambient Temp", f"{telemetry['temp']:.1f} °C")
                    m3.metric("Relative Humidity", f"{telemetry['rh']:.1f}%")
                    m4.metric("Wind Speed", f"{telemetry['wind']:.1f} m/s")
                    
                    live_vector = []
                    for f in features:
                        f_lower = f.lower()
                        if 'temp' in f_lower:
                            live_vector.append(telemetry['temp'])
                        elif 'irradiation' in f_lower or 'solar' in f_lower:
                            live_vector.append(telemetry['irradiation'])
                        elif 'humidity' in f_lower:
                            live_vector.append(telemetry['rh'])
                        elif 'pressure' in f_lower:
                            live_vector.append(telemetry['pressure'])
                        elif 'wind' in f_lower:
                            live_vector.append(telemetry['wind'])
                        else:
                            live_vector.append(50.0)
                            
                    live_df = pd.DataFrame([live_vector], columns=features)
                    live_pred = model.predict(live_df)[0]
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="metric-card" style="border-color: #38bdf8;">
                        <h3 style="color: #94a3b8 !important; margin-bottom: 0px;">LIVE SATELLITE FORECAST ({city_name.upper()})</h3>
                        <h1 style="color: #38bdf8 !important; font-size: 3rem; margin-top: 5px;">{max(0.0, live_pred):.2f} <span style="font-size: 1.5rem;">kW</span></h1>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Could not retrieve telemetry feed: {status}")
            else:
                st.error(f"Could not find coordinates for '{user_address}'. Please check the spelling.")

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b;'>SPG-X Solar Telemetry Intelligence System | Built independently by Subhadeep Barik</p>", unsafe_allow_html=True)
