import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
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
        background: rgba(30, 41, 59, 0.72);
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 22px;
        border-radius: 12px;
        backdrop-filter: blur(12px);
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .sub-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.22);
        padding: 16px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Pre-Loaded Instant Autocomplete Catalog (India + West Bengal + Global) ---
PRELOADED_PLACES = [
    "New Town, Rajarhat, Kolkata, West Bengal, India",
    "Salt Lake Sector V, Bidhannagar, Kolkata, West Bengal, India",
    "Techno India University, EM-4, Sector V, Salt Lake, Kolkata, India",
    "Haldia, Purba Medinipur, West Bengal, India",
    "Kolkata, West Bengal, India",
    "Howrah, West Bengal, India",
    "Durgapur, Paschim Bardhaman, West Bengal, India",
    "Asansol, Paschim Bardhaman, West Bengal, India",
    "Siliguri, Darjeeling, West Bengal, India",
    "Kharagpur, Paschim Medinipur, West Bengal, India",
    "Darjeeling, West Bengal, India",
    "Kalyani, Nadia, West Bengal, India",
    "Bardhaman, Purba Bardhaman, West Bengal, India",
    "Digha, Purba Medinipur, West Bengal, India",
    "Malda, West Bengal, India",
    "Krishnanagar, Nadia, West Bengal, India",
    "Bankura, West Bengal, India",
    "Purulia, West Bengal, India",
    "Midnapore, Paschim Medinipur, West Bengal, India",
    "Tamluk, Purba Medinipur, West Bengal, India",
    "Bhubaneswar, Odisha, India",
    "Cuttack, Odisha, India",
    "Puri, Odisha, India",
    "Rourkela, Odisha, India",
    "Ranchi, Jharkhand, India",
    "Jamshedpur, Jharkhand, India",
    "Dhanbad, Jharkhand, India",
    "Patna, Bihar, India",
    "Guwahati, Assam, India",
    "Shillong, Meghalaya, India",
    "Agartala, Tripura, India",
    "Gangtok, Sikkim, India",
    "New Delhi, Delhi, India",
    "Noida, Uttar Pradesh, India",
    "Gurugram, Haryana, India",
    "Mumbai, Maharashtra, India",
    "Navi Mumbai, Maharashtra, India",
    "Pune, Maharashtra, India",
    "Nagpur, Maharashtra, India",
    "Nashik, Maharashtra, India",
    "Bengaluru, Karnataka, India",
    "Mysuru, Karnataka, India",
    "Mangaluru, Karnataka, India",
    "Hyderabad, Telangana, India",
    "Warangal, Telangana, India",
    "Chennai, Tamil Nadu, India",
    "Coimbatore, Tamil Nadu, India",
    "Madurai, Tamil Nadu, India",
    "Tiruchirappalli, Tamil Nadu, India",
    "Ahmedabad, Gujarat, India",
    "Gandhinagar, Gujarat, India",
    "Surat, Gujarat, India",
    "Vadodara, Gujarat, India",
    "Rajkot, Gujarat, India",
    "Jaipur, Rajasthan, India",
    "Jodhpur, Rajasthan, India",
    "Udaipur, Rajasthan, India",
    "Jaisalmer, Rajasthan, India",
    "Bikaner, Rajasthan, India",
    "Lucknow, Uttar Pradesh, India",
    "Kanpur, Uttar Pradesh, India",
    "Varanasi, Uttar Pradesh, India",
    "Agra, Uttar Pradesh, India",
    "Prayagraj, Uttar Pradesh, India",
    "Bhopal, Madhya Pradesh, India",
    "Indore, Madhya Pradesh, India",
    "Gwalior, Madhya Pradesh, India",
    "Jabalpur, Madhya Pradesh, India",
    "Raipur, Chhattisgarh, India",
    "Visakhapatnam, Andhra Pradesh, India",
    "Vijayawada, Andhra Pradesh, India",
    "Tirupati, Andhra Pradesh, India",
    "Kochi, Kerala, India",
    "Thiruvananthapuram, Kerala, India",
    "Kozhikode, Kerala, India",
    "Chandigarh, India",
    "Amritsar, Punjab, India",
    "Ludhiana, Punjab, India",
    "Dehradun, Uttarakhand, India",
    "Haridwar, Uttarakhand, India",
    "Shimla, Himachal Pradesh, India",
    "Manali, Himachal Pradesh, India",
    "Srinagar, Jammu and Kashmir, India",
    "Jammu, Jammu and Kashmir, India",
    "Leh, Ladakh, India",
    "Panaji, Goa, India",
    "Puducherry, India",
    "Port Blair, Andaman and Nicobar Islands, India",
    "New York, NY, United States",
    "San Francisco, CA, United States",
    "Los Angeles, CA, United States",
    "Chicago, IL, United States",
    "London, United Kingdom",
    "Manchester, United Kingdom",
    "Tokyo, Japan",
    "Osaka, Japan",
    "Dubai, United Arab Emirates",
    "Abu Dhabi, United Arab Emirates",
    "Singapore, Singapore",
    "Sydney, NSW, Australia",
    "Melbourne, VIC, Australia",
    "Berlin, Germany",
    "Munich, Germany",
    "Paris, France",
    "Toronto, ON, Canada",
    "Zurich, Switzerland"
]

# Fast coordinate cache for instant zero-latency resolution on common places
INSTANT_COORDS = {
    "new town, rajarhat, kolkata, west bengal, india": (22.5867, 88.4750, "New Town, Kolkata, West Bengal, India"),
    "salt lake sector v, bidhannagar, kolkata, west bengal, india": (22.5726, 88.4312, "Salt Lake Sector V, Kolkata, West Bengal, India"),
    "techno india university, em-4, sector v, salt lake, kolkata, india": (22.5760, 88.4285, "Techno India University, Salt Lake, Kolkata, India"),
    "haldia, purba medinipur, west bengal, india": (22.0667, 88.0698, "Haldia, Purba Medinipur, West Bengal, India"),
    "kolkata, west bengal, india": (22.5726, 88.3639, "Kolkata, West Bengal, India"),
    "howrah, west bengal, india": (22.5958, 88.2636, "Howrah, West Bengal, India"),
    "durgapur, paschim bardhaman, west bengal, india": (23.5204, 87.3119, "Durgapur, West Bengal, India"),
    "asansol, paschim bardhaman, west bengal, india": (23.6739, 86.9524, "Asansol, West Bengal, India"),
    "siliguri, darjeeling, west bengal, india": (26.7271, 88.3953, "Siliguri, West Bengal, India"),
    "kharagpur, paschim medinipur, west bengal, india": (22.3460, 87.2320, "Kharagpur, West Bengal, India"),
    "darjeeling, west bengal, india": (27.0410, 88.2663, "Darjeeling, West Bengal, India"),
    "ahmedabad, gujarat, india": (23.0225, 72.5714, "Ahmedabad, Gujarat, India"),
    "new delhi, delhi, india": (28.6139, 77.2090, "New Delhi, Delhi, India"),
    "mumbai, maharashtra, india": (19.0760, 72.8777, "Mumbai, Maharashtra, India"),
    "bengaluru, karnataka, india": (12.9716, 77.5946, "Bengaluru, Karnataka, India"),
    "hyderabad, telangana, india": (17.3850, 78.4867, "Hyderabad, Telangana, India"),
    "chennai, tamil nadu, india": (13.0827, 80.2707, "Chennai, Tamil Nadu, India"),
    "pune, maharashtra, india": (18.5204, 73.8567, "Pune, Maharashtra, India"),
    "new york, ny, united states": (40.7128, -74.0060, "New York, NY, United States"),
    "london, united kingdom": (51.5074, -0.1278, "London, United Kingdom"),
    "tokyo, japan": (35.6762, 139.6503, "Tokyo, Japan"),
    "dubai, united arab emirates": (25.2048, 55.2708, "Dubai, United Arab Emirates"),
}

# --- 3. Data Loading & Random Forest Training ---
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

# --- 4. Triple-Engine Street, Landmark & City Geocoder ---
def score_relevance(item, query, bias_india=True):
    q = query.strip().lower()
    name = item.get("name", "").lower()
    label = item.get("label", "").lower()
    country = item.get("country", "").lower()

    score = 0
    if name == q:
        score += 120
    elif name.startswith(q):
        score += 80
    elif q in name:
        score += 50
    elif q in label:
        score += 30

    if bias_india and ("india" in country or item.get("countrycode") == "IN"):
        score += 65

    return score

@st.cache_data(ttl=900)
def smart_geocode_search(query, bias_india=True, gmaps_key=""):
    """
    Resolves any street address, college, landmark, PIN code, town, or city
    using Google Maps (if key provided) + Photon OSM Autocomplete + Nominatim + Open-Meteo.
    """
    if not query or not query.strip():
        return []

    clean_q = query.strip()
    lower_q = clean_q.lower()
    results = []
    seen_coords = set()

    def add_candidate(name, label, lat, lon, country=""):
        key = (round(float(lat), 2), round(float(lon), 2))
        if key not in seen_coords:
            seen_coords.add(key)
            results.append({
                "name": name,
                "label": label,
                "lat": float(lat),
                "lon": float(lon),
                "country": country
            })

    # 0. Instant match from curated cache
    if lower_q in INSTANT_COORDS:
        lat, lon, lbl = INSTANT_COORDS[lower_q]
        add_candidate(lbl.split(",")[0], lbl, lat, lon, lbl.split(",")[-1].strip())

    headers = {"User-Agent": "SPGX-Solar-Telemetry-Grid/3.0 (TechnoIndiaUniversity)"}

    # 1. Optional Google Maps Geocoding API (if user entered an API key)
    if gmaps_key and len(gmaps_key.strip()) > 10:
        try:
            g_url = "https://maps.googleapis.com/maps/api/geocode/json"
            g_params = {"address": clean_q, "key": gmaps_key.strip()}
            if bias_india:
                g_params["region"] = "in"
            g_res = requests.get(g_url, params=g_params, timeout=5)
            if g_res.status_code == 200:
                for item in g_res.json().get("results", [])[:6]:
                    loc = item.get("geometry", {}).get("location", {})
                    fmt = item.get("formatted_address", clean_q)
                    short_name = fmt.split(",")[0].strip()
                    add_candidate(short_name, fmt, loc.get("lat"), loc.get("lng"), fmt.split(",")[-1].strip())
        except Exception:
            pass

    # 2. Photon Komoot OpenStreetMap Autocomplete API (Streets, Universities, Landmarks, Towns)
    try:
        p_url = "https://photon.komoot.io/api/"
        p_params = {"q": clean_q, "limit": 8, "lang": "en"}
        if bias_india:
            p_params["lat"] = 22.5726
            p_params["lon"] = 88.3639
            p_params["location_bias_scale"] = 0.25
        p_res = requests.get(p_url, params=p_params, headers=headers, timeout=5)
        if p_res.status_code == 200:
            for feat in p_res.json().get("features", []):
                coords = feat.get("geometry", {}).get("coordinates", [0, 0])
                props = feat.get("properties", {})
                name = props.get("name") or props.get("street") or props.get("city") or clean_q
                parts = []
                for k in ["name", "street", "district", "locality", "city", "county", "state", "postcode", "country"]:
                    val = props.get(k)
                    if val and str(val) not in parts:
                        parts.append(str(val))
                label = ", ".join(parts) if parts else name
                add_candidate(name, label, coords[1], coords[0], props.get("country", ""))
    except Exception:
        pass

    # 3. OpenStreetMap Nominatim API (Deep Street / PIN code / Landmark search)
    try:
        n_url = "https://nominatim.openstreetmap.org/search"
        n_params = {"q": clean_q, "format": "jsonv2", "addressdetails": 1, "limit": 6, "accept-language": "en"}
        n_res = requests.get(n_url, params=n_params, headers=headers, timeout=5)
        if n_res.status_code == 200:
            for item in n_res.json():
                disp = item.get("display_name", "")
                name = item.get("name") or disp.split(",")[0].strip()
                addr = item.get("address", {})
                country = addr.get("country", "")
                short_parts = [p.strip() for p in disp.split(",")[:5]]
                if country and country not in short_parts:
                    short_parts.append(country)
                clean_label = ", ".join(short_parts)
                add_candidate(name, clean_label, item.get("lat"), item.get("lon"), country)
    except Exception:
        pass

    # 4. Open-Meteo Global Geocoder Fallback
    if len(results) < 2:
        try:
            om_url = "https://geocoding-api.open-meteo.com/v1/search"
            om_res = requests.get(om_url, params={"name": clean_q, "count": 6, "language": "en", "format": "json"}, timeout=5)
            if om_res.status_code == 200:
                for item in om_res.json().get("results", []):
                    name = item.get("name", clean_q)
                    admin1 = item.get("admin1", "")
                    country = item.get("country", "")
                    parts = [p for p in [name, admin1, country] if p]
                    add_candidate(name, ", ".join(parts), item.get("latitude"), item.get("longitude"), country)
        except Exception:
            pass

    results.sort(key=lambda x: score_relevance(x, clean_q, bias_india=bias_india), reverse=True)
    return results[:8]

# --- 5. Real-Time Solar & Weather Telemetry Engine ---
def fetch_realtime_solar_telemetry(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    current_vars = ",".join([
        "temperature_2m", "relative_humidity_2m", "pressure_msl",
        "precipitation", "snowfall", "cloud_cover", "cloud_cover_low",
        "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m",
        "wind_direction_10m", "wind_gusts_10m", "shortwave_radiation", "is_day"
    ])
    hourly_vars = ",".join([
        "temperature_2m", "relative_humidity_2m", "pressure_msl",
        "cloud_cover", "cloud_cover_low", "cloud_cover_mid",
        "cloud_cover_high", "wind_speed_10m", "wind_direction_10m",
        "wind_gusts_10m", "shortwave_radiation"
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

# --- 6. Dashboard Header ---
st.markdown("# ☀️ SPG-X: Solar Power Prediction Grid & Telemetry Dashboard")
st.markdown("Advanced photovoltaic power output forecasting & live street-level global meteorological telemetry.")

tab_live, tab_manual = st.tabs([
    "📡 Live Global Location & Satellite Telemetry",
    "🎛️ Manual Telemetry Controls & Feature Matrix"
])

# ==========================================
# TAB 1: UNIFIED GOOGLE-MAPS-STYLE LOCATION SEARCH
# ==========================================
with tab_live:
    if "custom_places" not in st.session_state:
        st.session_state.custom_places = []

    all_dropdown_options = st.session_state.custom_places + [
        p for p in PRELOADED_PLACES if p not in st.session_state.custom_places
    ]

    col_title, col_opts = st.columns([2.2, 1.2])
    with col_title:
        st.subheader("🌍 Smart Location & Landmark Search")
    with col_opts:
        bias_india = st.checkbox("🇮🇳 Prioritize India Results", value=True, help="Boosts Indian cities, towns, colleges, and PIN codes to the top.")

    # Single Unified Search Bar: Filters 100+ places live as you type OR accepts any custom street/landmark/PIN code
    try:
        user_selection = st.selectbox(
            "🔍 Type any Address, College, Landmark, PIN Code, or City (or pick from suggestions as you type):",
            options=all_dropdown_options,
            index=0,
            accept_new_options=True,
            placeholder="Start typing e.g. Haldia, Techno India, Salt Lake, Ahmedabad, 700156, New York..."
        )
    except TypeError:
        # Fallback if running on an older Streamlit version without accept_new_options
        c1, c2 = st.columns([1.6, 1.4])
        with c1:
            preset_pick = st.selectbox("🔍 Quick-Search 100+ Cities & Hubs:", options=all_dropdown_options, index=0)
        with c2:
            custom_typed = st.text_input("Or type any custom Street / Landmark / PIN Code:", value="")
        user_selection = custom_typed.strip() if custom_typed.strip() else preset_pick

    with st.expander("⚙️ Optional: Plug in Google Maps API Key (Not required — OpenStreetMap Photon & Nominatim active by default)"):
        gmaps_api_key = st.text_input("Google Maps Geocoding API Key (Optional):", value="", type="password")

    if user_selection:
        if user_selection not in all_dropdown_options:
            st.session_state.custom_places.insert(0, user_selection)

        matches = smart_geocode_search(user_selection, bias_india=bias_india, gmaps_key=gmaps_api_key)

        if matches:
            # If multiple distinct landmarks/areas match the query, show sleek 1-click selector pills
            if len(matches) > 1:
                match_labels = [f"📍 {m['label']}" for m in matches[:5]]
                chosen_pill = st.radio(
                    "✨ Closest Matching Locations (Click to switch):",
                    options=match_labels,
                    index=0,
                    horizontal=True
                )
                chosen_idx = match_labels.index(chosen_pill)
                target = matches[chosen_idx]
            else:
                target = matches[0]

            lat, lon = target["lat"], target["lon"]
            place_title = target["label"]
            short_name = target["name"]

            sim_peak_noon = st.checkbox(
                "☀️ Simulate Tomorrow's Peak Noon (12:00 PM) Forecast when location is currently at Night",
                value=False
            )

            with st.spinner(f"Synchronizing live satellite & meteorological feed for {place_title}..."):
                api_data, status = fetch_realtime_solar_telemetry(lat, lon)

            if api_data:
                current = api_data.get("current", {})
                tz_name = api_data.get("timezone", "UTC")
                local_time_str = current.get("time", "").replace("T", " ")
                is_day_now = int(current.get("is_day", 0))
                live_rad = float(current.get("shortwave_radiation", 0.0))

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
                    "☀️ PEAK NOON SIMULATION (12:0
