import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# --- 1. Page Configuration & Cyberpunk Styling ---
st.set_page_config(
    page_title="SPG-X // Solar Telemetry Grid",
    page_icon="☀️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #f8fafc;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 22px;
        border-radius: 12px;
        backdrop-filter: blur(12px);
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .sub-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.2);
        padding: 16px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Data Loading & Random Forest Training ---
@st.cache_resource
def load_and_train_model():
    dataset_path = "spg.csv"

    if not os.path.exists(dataset_path):
        np.random.seed(42)
        size = 600
        df = pd.DataFrame({
            "temperature_2_m_above_gnd": np.random.uniform(10, 42, size),
            "relative_humidity_2_m_above_gnd": np.random.uniform(20, 95, size),
            "mean_sea_level_pressure_MSL": np.random.uniform(995, 1025, size),
            "total_precipitation_sfc": np.random.uniform(0, 5, size),
            "snowfall_amount_sfc": np.zeros(size),
            "total_cloud_cover_sfc": np.random.uniform(0, 100, size),
            "high_cloud_cover_high_cld_lay": np.random.uniform(0, 100, size),
            "medium_cloud_cover_mid_cld_lay": np.random.uniform(0, 100, size),
            "low_cloud_cover_low_cld_lay": np.random.uniform(0, 100, size),
            "shortwave_radiation_backwards_sfc": np.random.uniform(0, 950, size),
            "wind_speed_10_m_above_gnd": np.random.uniform(0.5, 15, size),
            "wind_direction_10_m_above_gnd": np.random.uniform(0, 360, size),
            "wind_gust_10_m_above_gnd": np.random.uniform(1, 20, size),
            "angle_of_incidence": np.random.uniform(10, 80, size),
            "zenith": np.random.uniform(15, 85, size),
            "azimuth": np.random.uniform(90, 270, size),
        })
        df["generated_power_kw"] = (
            df["shortwave_radiation_backwards_sfc"] * 2.4
            - df["total_cloud_cover_sfc"] * 3.2
            - df["temperature_2_m_above_gnd"] * 4.5
            + np.random.normal(0, 25, size)
        ).clip(lower=0)
        df.to_csv(dataset_path, index=False)

    df = pd.read_csv(dataset_path)
    target_col = "generated_power_kw" if "generated_power_kw" in df.columns else df.columns[-1]
    feature_cols = [c for c in df.columns if c != target_col]

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    r2_score = model.score(X_test, y_test) * 100
    defaults = X.median().to_dict()
    mins = X.min().to_dict()
    maxs = X.max().to_dict()

    return model, feature_cols, r2_score, len(df), defaults, mins, maxs

model, features, model_r2, record_count, feat_defaults, feat_mins, feat_maxs = load_and_train_model()

# --- 3. Helper Functions for Global Geocoding & Live Telemetry ---
@st.cache_data(ttl=600)
def search_places_suggestions(query):
    """Fetches Google-Maps-style autocomplete suggestions for any town/city worldwide."""
    if not query or len(query.strip()) < 2:
        return []
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": query.strip(), "count": 8, "language": "en", "format": "json"}
    try:
        res = requests.get(url, params=params, timeout=6)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            suggestions = []
            for item in results:
                name = item.get("name", "")
                admin1 = item.get("admin1", "")
                country = item.get("country", "")
                lat = item.get("latitude")
                lon = item.get("longitude")
                tz = item.get("timezone", "UTC")
                label_parts = [p for p in [name, admin1, country] if p]
                label = f"{', '.join(label_parts)}  ({lat:.2f}°, {lon:.2f}°)"
                suggestions.append({
                    "label": label,
                    "name": name,
                    "admin1": admin1,
                    "country": country,
                    "lat": lat,
                    "lon": lon,
                    "timezone": tz
                })
            return suggestions
    except Exception:
        pass
    return []

def fetch_realtime_solar_telemetry(lat, lon):
    """Fetches real-time weather and solar radiation for exact coordinates."""
    url = "https://api.open-meteo.com/v1/forecast"
    current_vars = ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "pressure_msl",
        "precipitation",
        "snowfall",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "shortwave_radiation",
        "is_day"
    ])
    hourly_vars = ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "pressure_msl",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "shortwave_radiation"
    ])
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": current_vars,
        "hourly": hourly_vars,
        "timezone": "auto",
        "forecast_days": 2
    }
    try:
        res = requests.get(url, params=params, timeout=8)
        if res.status_code == 200:
            return res.json(), "OK"
        return None, f"API Error {res.status_code}"
    except Exception as e:
        return None, str(e)

def build_feature_vector(telemetry_dict):
    """Maps live meteorological telemetry to the exact columns of spg.csv."""
    rad = float(telemetry_dict.get("shortwave_radiation", 0.0))
    temp = float(telemetry_dict.get("temperature_2m", 25.0))
    rh = float(telemetry_dict.get("relative_humidity_2m", 50.0))
    pres = float(telemetry_dict.get("pressure_msl", 1013.0))
    precip = float(telemetry_dict.get("precipitation", 0.0))
    snow = float(telemetry_dict.get("snowfall", 0.0))
    cld_total = float(telemetry_dict.get("cloud_cover", 20.0))
    cld_low = float(telemetry_dict.get("cloud_cover_low", 10.0))
    cld_mid = float(telemetry_dict.get("cloud_cover_mid", 10.0))
    cld_high = float(telemetry_dict.get("cloud_cover_high", 10.0))
    ws = float(telemetry_dict.get("wind_speed_10m", 3.5))
    wd = float(telemetry_dict.get("wind_direction_10m", 180.0))
    wg = float(telemetry_dict.get("wind_gusts_10m", 5.0))
    is_day = int(telemetry_dict.get("is_day", 1 if rad > 5 else 0))

    # Dynamic solar geometry estimation from radiation intensity
    if is_day == 0 or rad <= 0:
        zenith, azimuth, aoi = 95.0, 180.0, 90.0
    else:
        norm_rad = min(max(rad / 1000.0, 0.05), 1.0)
        zenith = max(12.0, 82.0 * (1.0 - norm_rad * 0.75))
        azimuth = 180.0
        aoi = max(8.0, zenith * 0.85)

    row = {}
    for col in features:
        c = col.lower()
        if "shortwave" in c or "irradiation" in c or "solar" in c:
            row[col] = rad
        elif "temperature" in c or "temp" in c:
            row[col] = temp
        elif "humidity" in c:
            row[col] = rh
        elif "pressure" in c:
            row[col] = pres
        elif "precipitation" in c:
            row[col] = precip
        elif "snowfall" in c:
            row[col] = snow
        elif "high_cloud" in c:
            row[col] = cld_high
        elif "medium_cloud" in c or "mid_cld" in c:
            row[col] = cld_mid
        elif "low_cloud" in c:
            row[col] = cld_low
        elif "cloud" in c:
            row[col] = cld_total
        elif "wind_gust" in c:
            row[col] = wg
        elif "wind_speed" in c:
            if "900" in c:
                row[col] = ws * 1.25
            elif "80" in c:
                row[col] = ws * 1.4
            else:
                row[col] = ws
        elif "wind_direction" in c:
            row[col] = wd
        elif "zenith" in c:
            row[col] = zenith
        elif "azimuth" in c:
            row[col] = azimuth
        elif "incidence" in c:
            row[col] = aoi
        else:
            row[col] = feat_defaults.get(col, 0.0)

    return pd.DataFrame([row], columns=features)

# --- 4. Dashboard Header ---
st.markdown("# ☀️ SPG-X: Solar Power Prediction Grid & Telemetry Dashboard")
st.markdown("Advanced photovoltaic power output forecasting & live global meteorological telemetry.")

tab_live, tab_manual = st.tabs([
    "📡 Live Global Location & Satellite Telemetry",
    "🎛️ Manual Telemetry Controls & Feature Matrix"
])

# ==========================================
# TAB 1: LIVE SATELLITE & GLOBAL LOCATION SEARCH
# ==========================================
with tab_live:
    st.subheader("🌍 Intelligent Location Search & Real-Time Telemetry")
    st.markdown("Type any city, town, or district worldwide (e.g., **Haldia**, **Ahmedabad**, **Kolkata**, **New York**) to get live suggestions and real-time solar telemetry.")

    col_input, col_select = st.columns([1.2, 1.8], gap="medium")

    with col_input:
        search_query = st.text_input(
            "🔍 Type Location Name:",
            value="Haldia",
            placeholder="Type e.g. Haldia, Ahmedabad, Kolkata, Tokyo..."
        )

    suggestions = search_places_suggestions(search_query)

    with col_select:
        if suggestions:
            labels = [s["label"] for s in suggestions]
            selected_label = st.selectbox("📍 Select Matching Place (Auto-Suggested):", options=labels, index=0)
            selected_place = next(s for s in suggestions if s["label"] == selected_label)
        else:
            selected_place = None
            st.warning("No matching locations found. Try typing at least 2 characters or check spelling.")

    sim_peak_noon = st.checkbox(
        "☀️ Simulate Tomorrow's Peak Noon (12:00 PM) Forecast if target location is currently at Night",
        value=False
    )

    if selected_place:
        lat = selected_place["lat"]
        lon = selected_place["lon"]
        place_title = f"{selected_place['name']}, {selected_place['admin1']}, {selected_place['country']}".replace(", ,", ",")

        with st.spinner(f"Synchronizing live telemetry for {place_title}..."):
            api_data, status = fetch_realtime_solar_telemetry(lat, lon)

        if api_data:
            current = api_data.get("current", {})
            tz_name = api_data.get("timezone", "UTC")
            local_time_str = current.get("time", "").replace("T", " ")
            is_day_now = int(current.get("is_day", 0))
            live_rad = float(current.get("shortwave_radiation", 0.0))

            # Optional Peak Noon simulation for locations currently in nighttime
            using_noon_sim = False
            active_telemetry = current.copy()

            if sim_peak_noon and (is_day_now == 0 or live_rad <= 5.0):
                hourly = api_data.get("hourly", {})
                times = hourly.get("time", [])
                noon_idx = next((i for i, t in enumerate(times) if "T12:00" in t), None)
                if noon_idx is not None:
                    using_noon_sim = True
                    for k in [
                        "temperature_2m", "relative_humidity_2m", "pressure_msl",
                        "cloud_cover", "cloud_cover_low", "cloud_cover_mid",
                        "cloud_cover_high", "wind_speed_10m", "wind_direction_10m",
                        "wind_gusts_10m", "shortwave_radiation"
                    ]:
                        vals = hourly.get(k, [])
                        if noon_idx < len(vals) and vals[noon_idx] is not None:
                            active_telemetry[k] = vals[noon_idx]
                    active_telemetry["is_day"] = 1

            eff_is_day = int(active_telemetry.get("is_day", 0))
            eff_rad = float(active_telemetry.get("shortwave_radiation", 0.0))

            day_badge = (
                "☀️ PEAK NOON SIMULATION (12:00 PM LOCAL)" if using_noon_sim
                else ("☀️ DAYTIME FEED ACTIVE" if eff_is_day == 1 else "🌙 NIGHTTIME AT LOCATION (SOLAR IRRADIANCE = 0)")
            )

            st.success(
                f"📍 **Target Locked:** {place_title} | **Coords:** `{lat:.4f}°N, {lon:.4f}°E` | "
                f"**Local Time:** `{local_time_str} ({tz_name})` | **Status:** `{day_badge}`"
            )

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Solar Irradiance", f"{eff_rad:.1f} W/m²")
            m2.metric("Ambient Temp", f"{active_telemetry.get('temperature_2m', 0.0):.1f} °C")
            m3.metric("Relative Humidity", f"{active_telemetry.get('relative_humidity_2m', 0.0):.0f}%")
            m4.metric("Cloud Cover", f"{active_telemetry.get('cloud_cover', 0.0):.0f}%")
            m5.metric("Wind Speed (10m)", f"{active_telemetry.get('wind_speed_10m', 0.0):.1f} km/h")

            live_df = build_feature_vector(active_telemetry)

            # Strict physical zero enforcement when sun is down or irradiance is zero
            if eff_is_day == 0 or eff_rad <= 1.0:
                predicted_kw = 0.0
            else:
                predicted_kw = max(0.0, float(model.predict(live_df)[0]))

            st.markdown("<br>", unsafe_allow_html=True)
            status_note = (
                "🌙 Local Nighttime — Photovoltaic panels generate 0.00 kW after sunset. "
                "Check the box above to simulate tomorrow's Peak Noon (12:00 PM) output for this city!"
                if (eff_is_day == 0 or eff_rad <= 1.0)
                else "⚡ Live Random Forest inference computed from real-time satellite & meteorological feed."
            )

            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #94a3b8 !important; margin-bottom: 4px;">
                    ESTIMATED SOLAR POWER OUTPUT — {selected_place['name'].upper()}
                </h3>
                <h1 style="color: #38bdf8 !important; font-size: 3.4rem; margin: 8px 0;">
                    {predicted_kw:.2f} <span style="font-size: 1.6rem;">kW</span>
                </h1>
                <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 4px;">{status_note}</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🔎 Inspect Complete 20-Feature Telemetry Vector Sent to Model"):
                st.dataframe(live_df, use_container_width=True)
        else:
            st.error(f"Failed to fetch live weather telemetry: {status}")

# ==========================================
# TAB 2: MANUAL TELEMETRY & FEATURE IMPORTANCE
# ==========================================
with tab_manual:
    st.sidebar.header("⚙️ Manual Sensor Input Parameters")
    manual_inputs = {}
    for col in features:
        c_min = float(feat_mins.get(col, 0.0))
        c_max = float(feat_maxs.get(col, 1000.0))
        c_def = float(feat_defaults.get(col, (c_min + c_max) / 2.0))
        if c_min == c_max:
            c_max = c_min + 1.0
        manual_inputs[col] = st.sidebar.number_input(
            label=col,
            min_value=c_min,
            max_value=c_max * 1.5 if c_max > 0 else 100.0,
            value=c_def,
            step=max(0.01, round((c_max - c_min) / 100.0, 2))
        )

    manual_df = pd.DataFrame([manual_inputs], columns=features)
    manual_rad_cols = [c for c in features if "shortwave" in c.lower() or "irradiation" in c.lower()]
    manual_rad_val = float(manual_df[manual_rad_cols[0]].iloc[0]) if manual_rad_cols else 500.0
    manual_pred = 0.0 if manual_rad_val <= 0 else max(0.0, float(model.predict(manual_df)[0]))

    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        st.markdown(f"""
        <div class="sub-card">
            <h3>📊 Live System Telemetry Overview</h3>
            <p style="color: #94a3b8;">
                This command center processes multi-variable environmental feeds through a trained Random Forest regressor model.
                Use the sidebar controls to modify sensor inputs and execute custom solar output estimations.
            </p>
            <hr style="border-color: rgba(148,163,184,0.2);">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <span style="color: #64748b; font-size: 0.85rem;">MODEL ACCURACY (R² SCORE)</span><br>
                    <span style="color: #38bdf8; font-size: 1.6rem; font-weight: bold;">{model_r2:.2f}%</span>
                </div>
                <div style="text-align: right;">
                    <span style="color: #64748b; font-size: 0.85rem;">RECORDS: {record_count}</span><br>
                    <span style="color: #94a3b8; font-size: 0.95rem;">ALGORITHM: RF_REGRESSOR</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #94a3b8 !important; margin-bottom: 4px;">MANUAL SIMULATION OUTPUT</h3>
            <h1 style="color: #38bdf8 !important; font-size: 3.2rem; margin: 10px 0;">
                {manual_pred:.2f} <span style="font-size: 1.5rem;">kW</span>
            </h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🧬 Neural Feature Importance Matrix")
    st.caption("Relative weight and impact of each environmental sensor parameter on the Random Forest prediction model.")
    imp_df = pd.DataFrame({
        "Feature": features,
        "Importance": model.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    st.bar_chart(imp_df.set_index("Feature"))

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b;'>"
    "SPG-X Solar Telemetry Intelligence System | Built independently by Subhadeep Barik"
    "</p>",
    unsafe_allow_html=True
)
