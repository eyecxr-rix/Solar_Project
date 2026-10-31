import html
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="SPG-X // Enterprise Solar Telemetry & Forecasting",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 2. CORPORATE DESIGN SYSTEM (CALIBSUN x METEOSOURCE CSS & ANIMATIONS)
# ==============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap');

:root {
    --bg-base: #06090f;
    --bg-panel: rgba(11, 17, 30, 0.78);
    --bg-panel-solid: #0b111e;
    --border-subtle: rgba(148, 163, 184, 0.14);
    --border-hover: rgba(245, 158, 11, 0.55);
    --accent-amber: #f59e0b;
    --accent-cyan: #0ea5e9;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

.stApp {
    background-color: var(--bg-base);
    background-image: 
        radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.06) 0px, transparent 45%),
        radial-gradient(at 100% 0%, rgba(245, 158, 11, 0.06) 0px, transparent 45%),
        linear-gradient(rgba(148, 163, 184, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148, 163, 184, 0.025) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding-top: 1.4rem !important;
    padding-bottom: 3rem !important;
    max-width: 1440px !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

@keyframes revealUp {
    0% { opacity: 0; transform: translateY(12px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes statusPulse {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.55); }
    70% { box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Top Enterprise Header Banner */
.corp-header {
    position: relative;
    border-radius: 12px;
    background: 
        linear-gradient(95deg, rgba(6, 9, 15, 0.96) 0%, rgba(11, 17, 30, 0.88) 55%, rgba(15, 23, 42, 0.72) 100%),
        url('https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=1800&q=80') center 35% / cover no-repeat;
    border: 1px solid var(--border-subtle);
    padding: 1.65rem 2.1rem;
    margin-bottom: 0.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1.25rem;
    animation: revealUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.corp-header::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-amber) 0%, var(--accent-cyan) 50%, transparent 100%);
    border-radius: 12px 12px 0 0;
}

.brand-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent-amber);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.4rem;
}

.pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    display: inline-block;
    animation: statusPulse 2.2s infinite;
}

.brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.72rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #ffffff;
    margin: 0 0 0.25rem 0;
}

.brand-subtitle {
    color: var(--text-secondary);
    font-size: 0.86rem;
    margin: 0;
    max-width: 680px;
}

.header-meta-grid {
    display: flex;
    gap: 1.4rem;
    background: rgba(6, 9, 15, 0.78);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.7rem 1.2rem;
}

.meta-item {
    display: flex;
    flex-direction: column;
}

.meta-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
}

.meta-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-top: 2px;
}

/* Powered By // Supporting API Ticker Strip */
.api-strip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.65rem;
    background: rgba(11, 17, 30, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 8px;
    padding: 0.55rem 1.1rem;
    margin-bottom: 1.1rem;
}

.api-strip-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
}

.api-badges-wrap {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.api-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #cbd5e1;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.18);
    padding: 3px 10px;
    border-radius: 5px;
    transition: all 0.22s ease;
}

.api-badge:hover {
    border-color: var(--accent-amber);
    color: #ffffff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.12);
}

.api-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent-amber);
}

/* Segmented Corporate Tabs */
div[data-testid="stTabs"] > div[role="tablist"] {
    background: var(--bg-panel-solid);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 5px;
    gap: 6px;
    margin-bottom: 1.15rem;
}

div[data-testid="stTabs"] button[role="tab"] {
    border-radius: 7px !important;
    padding: 0.52rem 1.2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stTabs"] button[role="tab"]:hover {
    color: var(--text-primary) !important;
    background: rgba(255, 255, 255, 0.03) !important;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: rgba(245, 158, 11, 0.12) !important;
    color: #ffffff !important;
    border: 1px solid rgba(245, 158, 11, 0.4) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}

div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
    display: none !important;
}

/* Section Panels & Glass Cards */
.corp-panel {
    background: var(--bg-panel);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 1rem;
    transition: border-color 0.25s ease, transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    animation: revealUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.corp-panel:hover {
    border-color: rgba(148, 163, 184, 0.28);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.panel-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

.panel-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    color: var(--text-muted);
    background: rgba(148, 163, 184, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.14);
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}

/* KPI Telemetry Ribbon Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.85rem;
    margin-bottom: 1rem;
}

@media (max-width: 1100px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

.kpi-card {
    background: var(--bg-panel);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 0.95rem 1.1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    animation: revealUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.kpi-card::after {
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-amber), var(--accent-cyan));
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.kpi-card:hover {
    transform: translateY(-4px);
    border-color: var(--border-hover);
    box-shadow: 0 12px 28px -8px rgba(0, 0, 0, 0.6), 0 0 18px rgba(245, 158, 11, 0.08);
}

.kpi-card:hover::after {
    transform: scaleX(1);
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}

.kpi-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
}

.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.42rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.2;
}

.kpi-unit {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-left: 3px;
}

.kpi-sub {
    font-size: 0.71rem;
    color: var(--text-muted);
    margin-top: 0.32rem;
}

/* Primary Power Yield Readout Banner */
.yield-hero {
    background: linear-gradient(125deg, rgba(11, 17, 30, 0.95) 0%, rgba(15, 23, 42, 0.9) 60%, rgba(245, 158, 11, 0.12) 100%);
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-left: 4px solid var(--accent-amber);
    border-radius: 10px;
    padding: 1.35rem 1.7rem;
    margin-bottom: 1.05rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.55);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.yield-hero:hover {
    box-shadow: 0 18px 42px -10px rgba(245, 158, 11, 0.16);
}

.yield-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent-amber);
    margin-bottom: 0.25rem;
}

.yield-location {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.12rem;
    font-weight: 600;
    color: var(--text-primary);
}

.yield-note {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

.yield-number-box {
    text-align: right;
}

.yield-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.65rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1;
    letter-spacing: -0.03em;
}

.yield-unit {
    font-size: 1.05rem;
    font-weight: 500;
    color: var(--accent-amber);
    margin-left: 6px;
}

/* Telemetry Status Strip */
.telemetry-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.75rem;
    background: rgba(11, 17, 30, 0.9);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.62rem 1.05rem;
    margin-bottom: 0.95rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-secondary);
}

.status-pill-day {
    background: rgba(245, 158, 11, 0.14);
    border: 1px solid rgba(245, 158, 11, 0.45);
    color: #fbbf24;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 600;
}

.status-pill-night {
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.4);
    color: #38bdf8;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 600;
}

/* Footer Architecture Grid (Powered By Section) */
.arch-footer {
    margin-top: 2.2rem;
    padding-top: 1.4rem;
    border-top: 1px solid var(--border-subtle);
}

.arch-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.85rem;
    margin-top: 0.8rem;
}

@media (max-width: 1000px) {
    .arch-grid { grid-template-columns: repeat(2, 1fr); }
}

.arch-card {
    background: rgba(11, 17, 30, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 8px;
    padding: 0.9rem 1.05rem;
    transition: all 0.25s ease;
}

.arch-card:hover {
    border-color: rgba(245, 158, 11, 0.45);
    transform: translateY(-2px);
}

.arch-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--accent-amber);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.arch-provider {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0.2rem 0;
}

.arch-desc {
    font-size: 0.73rem;
    color: var(--text-muted);
    line-height: 1.4;
}

/* Input Controls Refinement */
div[data-testid="stNumberInput"] > div > div > input,
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stSelectbox"] > div > div {
    background-color: #090e1a !important;
    border: 1px solid rgba(148, 163, 184, 0.22) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.84rem !important;
}

div[data-testid="stNumberInput"] > div > div > input:focus,
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent-amber) !important;
    box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.15) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. MODEL, DATASET & FEATURE DEFINITIONS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "solar_model.pkl"
CSV_PATH = BASE_DIR / "spg.csv"

# Base reference coordinates for "Prioritize Nearby Areas" (New Town / Kolkata Hub)
HOME_BASE_LAT = 22.5867
HOME_BASE_LON = 88.4750

FEATURE_SCHEMA = [
    ("temperature_2_m_above_gnd", "Ambient Temperature (2m)", "degC", 14.75, "Surface Meteorology"),
    ("relative_humidity_2_m_above_gnd", "Relative Humidity (2m)", "%", 48.0, "Surface Meteorology"),
    ("mean_sea_level_pressure_MSL", "Sea Level Pressure (MSL)", "hPa", 1018.1, "Surface Meteorology"),
    ("total_precipitation_sfc", "Surface Precipitation", "mm", 0.0, "Surface Meteorology"),
    ("snowfall_amount_sfc", "Snowfall Amount", "mm", 0.0, "Surface Meteorology"),
    ("total_cloud_cover_sfc", "Total Cloud Cover", "%", 8.7, "Atmospheric Cloud Layers"),
    ("high_cloud_cover_high_cld_lay", "High-Altitude Cloud Layer", "%", 0.0, "Atmospheric Cloud Layers"),
    ("medium_cloud_cover_mid_cld_lay", "Mid-Altitude Cloud Layer", "%", 0.0, "Atmospheric Cloud Layers"),
    ("low_cloud_cover_low_cld_lay", "Low-Altitude Cloud Layer", "%", 0.0, "Atmospheric Cloud Layers"),
    ("shortwave_radiation_backwards_sfc", "Shortwave Solar Irradiance", "W/m2", 381.81, "Solar Geometry & Flux"),
    ("wind_speed_10_m_above_gnd", "Wind Speed (10m Anemometer)", "km/h", 14.46, "Multi-Altitude Wind Profile"),
    ("wind_direction_10_m_above_gnd", "Wind Direction (10m)", "deg", 191.77, "Multi-Altitude Wind Profile"),
    ("wind_speed_80_m_above_gnd", "Wind Speed (80m Hub Height)", "km/h", 16.24, "Multi-Altitude Wind Profile"),
    ("wind_direction_80_m_above_gnd", "Wind Direction (80m)", "deg", 187.77, "Multi-Altitude Wind Profile"),
    ("wind_speed_900_mb", "Upper Wind Speed (900 mb)", "km/h", 14.49, "Multi-Altitude Wind Profile"),
    ("wind_direction_900_mb", "Upper Wind Direction (900 mb)", "deg", 187.99, "Multi-Altitude Wind Profile"),
    ("wind_gust_10_m_above_gnd", "Surface Wind Gust (10m)", "km/h", 18.0, "Multi-Altitude Wind Profile"),
    ("angle_of_incidence", "PV Angle of Incidence (AOI)", "deg", 47.34, "Solar Geometry & Flux"),
    ("zenith", "Solar Zenith Angle", "deg", 62.14, "Solar Geometry & Flux"),
    ("azimuth", "Solar Azimuth Angle", "deg", 163.24, "Solar Geometry & Flux"),
]

FEATURE_COLUMNS = [item[0] for item in FEATURE_SCHEMA]
DEFAULT_TELEMETRY = {item[0]: item[3] for item in FEATURE_SCHEMA}

CURATED_NEARBY_HUBS = [
    {"label": "New Town, Rajarhat, Kolkata, West Bengal, India", "short_name": "New Town, Kolkata", "lat": 22.5867, "lon": 88.4750, "country": "India"},
    {"label": "Haldia Industrial Belt, Purba Medinipur, West Bengal, 721604, India", "short_name": "Haldia, West Bengal", "lat": 22.0667, "lon": 88.0698, "country": "India"},
    {"label": "Salt Lake Sector V (Bidhannagar), Kolkata, West Bengal, 700091, India", "short_name": "Salt Lake Sector V", "lat": 22.5726, "lon": 88.4312, "country": "India"},
    {"label": "IIT Kharagpur Campus, Kharagpur, West Bengal, 721302, India", "short_name": "Kharagpur, WB", "lat": 22.3149, "lon": 87.3105, "country": "India"},
    {"label": "Durgapur Steel & Solar Grid, Paschim Bardhaman, West Bengal, India", "short_name": "Durgapur, WB", "lat": 23.5204, "lon": 87.3119, "country": "India"},
    {"label": "Kolaghat Thermal & Solar Substation, Purba Medinipur, West Bengal, India", "short_name": "Kolaghat, WB", "lat": 22.4270, "lon": 87.8710, "country": "India"},
    {"label": "Sagardighi Power Grid, Murshidabad, West Bengal, 742226, India", "short_name": "Sagardighi, WB", "lat": 24.3769, "lon": 88.0886, "country": "India"},
    {"label": "Bhadla Utility Solar Park, Phalodi, Rajasthan, India", "short_name": "Bhadla Solar Park", "lat": 27.5362, "lon": 71.9167, "country": "India"},
]


@st.cache_resource(show_spinner=False)
def load_solar_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


@st.cache_data(show_spinner=False)
def load_reference_bounds():
    if CSV_PATH.exists():
        try:
            df = pd.read_csv(CSV_PATH)
            bounds = {}
            for col in FEATURE_COLUMNS:
                if col in df.columns:
                    bounds[col] = (
                        float(df[col].min()),
                        float(df[col].max()),
                        float(df[col].median()),
                    )
            return bounds
        except Exception:
            pass
    return {}


model = load_solar_model()
feature_bounds = load_reference_bounds()


# ==============================================================================
# 4. GEOMETRY,HAVERSINE DISTANCE & MULTI-ENGINE GEOCODING
# ==============================================================================
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def compute_solar_angles(lat: float, lon: float, dt_utc: datetime, panel_tilt: float = 25.0, panel_azimuth: float = 180.0):
    day_of_year = dt_utc.timetuple().tm_yday
    hour_decimal = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0

    gamma = 2.0 * math.pi / 365.0 * (day_of_year - 1 + (hour_decimal - 12.0) / 24.0)
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )

    time_offset = eqtime + 4.0 * lon
    tst = hour_decimal * 60.0 + time_offset
    ha_deg = (tst / 4.0) - 180.0
    ha_rad = math.radians(ha_deg)
    lat_rad = math.radians(lat)

    cos_zenith = math.sin(lat_rad) * math.sin(decl) + math.cos(lat_rad) * math.cos(decl) * math.cos(ha_rad)
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    zenith_rad = math.acos(cos_zenith)
    zenith_deg = math.degrees(zenith_rad)

    sin_zenith = math.sin(zenith_rad)
    if sin_zenith > 1e-5:
        cos_az = (math.sin(decl) * math.cos(lat_rad) - math.cos(decl) * math.sin(lat_rad) * math.cos(ha_rad)) / sin_zenith
        cos_az = max(-1.0, min(1.0, cos_az))
        az_deg = math.degrees(math.acos(cos_az))
        if ha_deg > 0:
            az_deg = 360.0 - az_deg
    else:
        az_deg = 180.0

    tilt_rad = math.radians(panel_tilt)
    surf_az_rad = math.radians(panel_azimuth)
    az_rad = math.radians(az_deg)
    cos_aoi = math.cos(zenith_rad) * math.cos(tilt_rad) + math.sin(zenith_rad) * math.sin(tilt_rad) * math.cos(az_rad - surf_az_rad)
    cos_aoi = max(-1.0, min(1.0, cos_aoi))
    aoi_deg = math.degrees(math.acos(cos_aoi))

    return round(zenith_deg, 2), round(az_deg, 2), round(aoi_deg, 2)


def build_feature_vector(telemetry_dict: dict) -> pd.DataFrame:
    row = {}
    for col in FEATURE_COLUMNS:
        val = telemetry_dict.get(col, DEFAULT_TELEMETRY[col])
        row[col] = float(val) if val is not None else float(DEFAULT_TELEMETRY[col])
    if model is not None and hasattr(model, "feature_names_in_"):
        ordered = [c for c in model.feature_names_in_ if c in row]
        return pd.DataFrame([row])[ordered]
    return pd.DataFrame([row])[FEATURE_COLUMNS]


def predict_power_kw(telemetry_dict: dict, is_day: int = 1, geometry_scale: float = 1.0) -> float:
    rad = float(telemetry_dict.get("shortwave_radiation_backwards_sfc", 0.0))
    if is_day == 0 or rad <= 0.0:
        return 0.0
    if model is None:
        return max(0.0, rad * 2.45 * geometry_scale)
    X_vec = build_feature_vector(telemetry_dict)
    pred = float(model.predict(X_vec)[0])
    return max(0.0, pred * geometry_scale)


@st.cache_data(ttl=900, show_spinner=False)
def search_locations_multi_engine(
    query: str,
    prioritize_india: bool = True,
    prioritize_nearby: bool = True,
    gmaps_api_key: str = "",
):
    """Fetch relevant suggestions from Google Maps (if key provided), OpenStreetMap Nominatim, and Komoot Photon."""
    q = (query or "").strip()
    if len(q) < 2:
        return CURATED_NEARBY_HUBS[:6]

    results = []
    seen_coords = set()
    headers = {"User-Agent": "SPGX-Enterprise-Solar-Telemetry/3.0"}

    def add_candidate(label: str, short_name: str, lat: float, lon: float, country: str, source_tag: str):
        key = (round(lat, 2), round(lon, 2))
        if key in seen_coords:
            return
        seen_coords.add(key)
        dist_km = haversine_km(HOME_BASE_LAT, HOME_BASE_LON, lat, lon)
        results.append(
            {
                "label": label,
                "short_name": short_name,
                "lat": lat,
                "lon": lon,
                "country": country,
                "dist_km": dist_km,
                "source": source_tag,
            }
        )

    # 1. Match from Curated Local / India Hubs first if query matches
    for hub in CURATED_NEARBY_HUBS:
        if q.lower() in hub["label"].lower() or q.lower() in hub["short_name"].lower():
            add_candidate(hub["label"], hub["short_name"], hub["lat"], hub["lon"], hub["country"], "GRID-HUB")

    # 2. Google Maps Geocoding API (if user entered a key)
    if gmaps_api_key.strip():
        try:
            g_params = {"address": q, "key": gmaps_api_key.strip()}
            if prioritize_india:
                g_params["region"] = "in"
            r_g = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=g_params, timeout=5)
            if r_g.status_code == 200:
                for item in r_g.json().get("results", [])[:5]:
                    loc = item.get("geometry", {}).get("location", {})
                    fmt = item.get("formatted_address", q)
                    short = fmt.split(",")[0].strip()
                    add_candidate(fmt, short, float(loc["lat"]), float(loc["lng"]), "India" if "india" in fmt.lower() else "", "GMAPS")
        except Exception:
            pass

    # 3. OpenStreetMap Nominatim (Great for Indian districts, landmarks, colleges, PIN codes)
    try:
        nom_params = {
            "q": q,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 6,
        }
        if prioritize_india and not prioritize_nearby:
            nom_params["countrycodes"] = "in"
        elif prioritize_nearby:
            # Viewbox around West Bengal / Eastern India while still allowing broader matches
            nom_params["viewbox"] = "85.5,27.5,90.0,20.5"
            nom_params["bounded"] = 0

        r_nom = requests.get("https://nominatim.openstreetmap.org/search", params=nom_params, headers=headers, timeout=6)
        if r_nom.status_code == 200:
            for item in r_nom.json():
                disp = item.get("display_name", "")
                addr = item.get("address", {})
                short = (
                    item.get("name")
                    or addr.get("city")
                    or addr.get("town")
                    or addr.get("suburb")
                    or addr.get("county")
                    or disp.split(",")[0]
                )
                country = addr.get("country", "")
                add_candidate(disp, short, float(item["lat"]), float(item["lon"]), country, "OSM")
    except Exception:
        pass

    # 4. Komoot Photon Geocoder (With spatial bias toward user's nearby hub when prioritize_nearby is active)
    try:
        ph_params = {"q": q, "limit": 6}
        if prioritize_nearby:
            ph_params["lat"] = HOME_BASE_LAT
            ph_params["lon"] = HOME_BASE_LON
        r_ph = requests.get("https://photon.komoot.io/api/", params=ph_params, headers=headers, timeout=6)
        if r_ph.status_code == 200:
            for f in r_ph.json().get("features", []):
                props = f.get("properties", {})
                coords = f.get("geometry", {}).get("coordinates", [HOME_BASE_LON, HOME_BASE_LAT])
                parts = [
                    props.get("name"),
                    props.get("street"),
                    props.get("district"),
                    props.get("city"),
                    props.get("state"),
                    props.get("postcode"),
                    props.get("country"),
                ]
                label = ", ".join([str(p) for p in dict.fromkeys(parts) if p])
                short = props.get("name") or props.get("city") or props.get("district") or q
                if label:
                    add_candidate(label, short, float(coords[1]), float(coords[0]), props.get("country", ""), "PHOTON")
    except Exception:
        pass

    if not results:
        for hub in CURATED_NEARBY_HUBS[:4]:
            add_candidate(hub["label"], hub["short_name"], hub["lat"], hub["lon"], hub["country"], "FALLBACK")

    # Sort logic: Nearby priority & India priority
    def sort_key(item):
        is_india = 0 if ("india" in item.get("country", "").lower() or "india" in item["label"].lower()) else 1
        dist = item.get("dist_km", 99999.0)
        is_nearby_ring = 0 if dist <= 350.0 else 1
        if prioritize_nearby and prioritize_india:
            return (is_india, is_nearby_ring, dist)
        elif prioritize_nearby:
            return (is_nearby_ring, dist)
        elif prioritize_india:
            return (is_india, dist)
        return (0, 0)

    results.sort(key=sort_key)
    return results[:8]


@st.cache_data(ttl=600, show_spinner=False)
def fetch_open_meteo_telemetry(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    hourly_vars = [
        "temperature_2m",
        "relative_humidity_2m",
        "pressure_msl",
        "precipitation",
        "snowfall",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "shortwave_radiation",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_speed_80m",
        "wind_direction_80m",
        "wind_gusts_10m",
        "is_day",
    ]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join(hourly_vars),
        "hourly": ",".join(hourly_vars),
        "forecast_days": 3,
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_nasa_power_recent(lat: float, lon: float):
    end_dt = datetime.now(timezone.utc).date() - timedelta(days=2)
    start_dt = end_dt - timedelta(days=30)
    url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,PS,WS10M,WD10M,PRECTOTCORR",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start_dt.strftime("%Y%m%d"),
        "end": end_dt.strftime("%Y%m%d"),
        "format": "JSON",
        "time-standard": "UTC",
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    payload = r.json()
    param_data = payload.get("properties", {}).get("parameter", {})
    if not param_data or "ALLSKY_SFC_SW_DWN" not in param_data:
        return pd.DataFrame()

    records = []
    rad_dict = param_data["ALLSKY_SFC_SW_DWN"]
    for ts_key, rad_val in rad_dict.items():
        if rad_val is None or float(rad_val) < -90:
            continue
        dt_obj = datetime.strptime(ts_key, "%Y%m%d%H").replace(tzinfo=timezone.utc)
        t2m = float(param_data.get("T2M", {}).get(ts_key, 20.0))
        rh2m = float(param_data.get("RH2M", {}).get(ts_key, 50.0))
        ps_kpa = float(param_data.get("PS", {}).get(ts_key, 101.3))
        ws10_ms = float(param_data.get("WS10M", {}).get(ts_key, 3.5))
        wd10 = float(param_data.get("WD10M", {}).get(ts_key, 180.0))
        prec = float(param_data.get("PRECTOTCORR", {}).get(ts_key, 0.0))

        ps_hpa = ps_kpa * 10.0 if ps_kpa < 200 else ps_kpa
        ws10_kmh = max(0.0, ws10_ms * 3.6)
        zen, az, aoi = compute_solar_angles(lat, lon, dt_obj)

        tele = dict(DEFAULT_TELEMETRY)
        tele.update(
            {
                "temperature_2_m_above_gnd": t2m if t2m > -90 else 20.0,
                "relative_humidity_2_m_above_gnd": max(0.0, min(100.0, rh2m if rh2m > -90 else 50.0)),
                "mean_sea_level_pressure_MSL": ps_hpa,
                "total_precipitation_sfc": max(0.0, prec if prec > -90 else 0.0),
                "shortwave_radiation_backwards_sfc": max(0.0, float(rad_val)),
                "wind_speed_10_m_above_gnd": ws10_kmh,
                "wind_direction_10_m_above_gnd": wd10 if wd10 >= 0 else 180.0,
                "wind_speed_80_m_above_gnd": ws10_kmh * 1.18,
                "wind_direction_80_m_above_gnd": wd10 if wd10 >= 0 else 180.0,
                "wind_speed_900_mb": ws10_kmh * 1.25,
                "wind_direction_900_mb": wd10 if wd10 >= 0 else 180.0,
                "wind_gust_10_m_above_gnd": ws10_kmh * 1.35,
                "zenith": zen,
                "azimuth": az,
                "angle_of_incidence": aoi,
            }
        )
        is_day_flag = 1 if float(rad_val) > 2.0 else 0
        pred_kw = predict_power_kw(tele, is_day=is_day_flag)
        records.append(
            {
                "timestamp": dt_obj,
                "irradiance_wm2": max(0.0, float(rad_val)),
                "temp_c": tele["temperature_2_m_above_gnd"],
                "wind_kmh": ws10_kmh,
                "predicted_kw": pred_kw,
            }
        )

    df_nasa = pd.DataFrame(records)
    if not df_nasa.empty:
        df_nasa = df_nasa.sort_values("timestamp").tail(168).reset_index(drop=True)
    return df_nasa


# ==============================================================================
# 5. ENTERPRISE HEADER & "POWERED BY" SUPPORTING API RIBBON
# ==============================================================================
utc_now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
model_status_label = "RF-ENSEMBLE // ONLINE" if model is not None else "PHYSICS FALLBACK"

st.markdown(
    f"""
<div class="corp-header">
    <div>
        <div class="brand-eyebrow">
            <span class="pulse-dot"></span> SPG-X // UTILITY-SCALE PHOTOVOLTAIC TELEMETRY &amp; FORECASTING
        </div>
        <h1 class="brand-title">Solar Power Prediction Grid &amp; Telemetry Workbench</h1>
        <p class="brand-subtitle">
            High-resolution atmospheric boundary-layer modeling, real-time satellite irradiance synthesis, and machine-learning yield dispatch.
        </p>
    </div>
    <div class="header-meta-grid">
        <div class="meta-item">
            <span class="meta-label">INFERENCE ENGINE</span>
            <span class="meta-val">{model_status_label}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">TELEMETRY STREAM</span>
            <span class="meta-val">OPEN-METEO / NASA POWER</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">SYSTEM CLOCK</span>
            <span class="meta-val">{utc_now_str}</span>
        </div>
    </div>
</div>

<!-- Powered By & Supporting APIs Bar -->
<div class="api-strip">
    <div class="api-strip-label">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        POWERED BY // SUPPORTING TELEMETRY &amp; GEOSPATIAL APIS
    </div>
    <div class="api-badges-wrap">
        <span class="api-badge"><span class="api-dot"></span>Open-Meteo Weather API</span>
        <span class="api-badge"><span class="api-dot"></span>NASA LaRC POWER Satellite</span>
        <span class="api-badge"><span class="api-dot"></span>Google Maps &amp; OSM Nominatim</span>
        <span class="api-badge"><span class="api-dot"></span>Komoot Photon Geocoder</span>
        <span class="api-badge"><span class="api-dot"></span>Scikit-Learn RF Ensemble</span>
        <span class="api-badge"><span class="api-dot"></span>Plotly WebGL &amp; CARTO Maps</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 6. MAIN NAVIGATION WORKBENCH TABS
# ==============================================================================
tab_live, tab_matrix, tab_nasa = st.tabs(
    [
        "01 // LIVE GLOBAL TELEMETRY & FORECAST",
        "02 // MANUAL TELEMETRY & FEATURE MATRIX",
        "03 // NASA POWER HISTORICAL VALIDATION",
    ]
)

# ------------------------------------------------------------------------------
# TAB 1: LIVE GLOBAL TELEMETRY & SPATIAL WORKBENCH
# ------------------------------------------------------------------------------
with tab_live:
    col_left, col_right = st.columns([1.08, 1.92], gap="large")

    with col_left:
        st.markdown(
            """
        <div class="corp-panel">
            <div class="panel-header">
                <div class="panel-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"/></svg>
                    Spatial Target &amp; Array Configuration
                </div>
                <span class="panel-tag">MULTI-GEOCODER ACTIVE</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

        if "search_query_state" not in st.session_state:
            st.session_state.search_query_state = "New Town, Rajarhat, Kolkata"

        # Quick-Jump Nearby & Regional Solar Hubs
        st.caption("Quick-Jump Regional & Nearby Grid Targets:")
        q_cols = st.columns(4)
        quick_presets = [
            ("New Town", "New Town, Rajarhat, Kolkata"),
            ("Haldia", "Haldia, Purba Medinipur, West Bengal"),
            ("Kharagpur", "IIT Kharagpur, West Bengal"),
            ("Durgapur", "Durgapur, West Bengal"),
        ]
        for idx, (btn_label, preset_q) in enumerate(quick_presets):
            with q_cols[idx]:
                if st.button(btn_label, key=f"preset_{idx}", use_container_width=True):
                    st.session_state.search_query_state = preset_q

        search_q = st.text_input(
            "Search Substation, Landmark, College, PIN Code, or City",
            value=st.session_state.search_query_state,
            placeholder="e.g., Haldia, Jadavpur University, Salt Lake, Bhadla...",
        )
        st.session_state.search_query_state = search_q

        # Priority Checkboxes: Nearby Areas + India Grid + Noon Sim
        c_opt1, c_opt2, c_opt3 = st.columns(3)
        with c_opt1:
            prio_nearby = st.checkbox(
                "Prioritize Nearby",
                value=True,
                help="Sorts matches by proximity (km) to your local West Bengal / Kolkata grid hub.",
            )
        with c_opt2:
            prio_india = st.checkbox(
                "Prioritize India",
                value=True,
                help="Biases geocoding results to Indian states, PIN codes, and substations.",
            )
        with c_opt3:
            sim_noon = st.checkbox(
                "Peak Noon (12:00)",
                value=False,
                help="Simulates 12:00 PM solar flux when target location is currently at night.",
            )

        with st.expander("Optional: Plug in Google Maps Geocoding API Key"):
            gmaps_key = st.text_input(
                "Google Maps API Key (Leave blank for default OSM Nominatim + Photon)",
                value="",
                type="password",
            )

        candidates = search_locations_multi_engine(
            search_q,
            prioritize_india=prio_india,
            prioritize_nearby=prio_nearby,
            gmaps_api_key=gmaps_key,
        )

        # Build formatted suggestion labels with distance & source tag
        formatted_options = []
        option_map = {}
        for c in candidates:
            dist_str = f"{c['dist_km']:.0f} km" if c.get("dist_km") is not None else ""
            disp_str = f"{c['label']}  [{dist_str} • {c.get('source', 'GEO')}]"
            formatted_options.append(disp_str)
            option_map[disp_str] = c

        selected_disp = st.radio(
            f"Relevant Matching Locations ({len(formatted_options)} found — click to lock target):",
            options=formatted_options,
            index=0,
        )
        active_loc = option_map.get(selected_disp, candidates[0])

        lat_val = active_loc["lat"]
        lon_val = active_loc["lon"]
        short_name = active_loc["short_name"]

        st.markdown("##### PV Hardware Geometry")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            panel_tilt = st.slider("Module Tilt (deg)", 0, 75, 25)
        with g_col2:
            panel_az = st.slider("Module Azimuth (deg)", 90, 270, 180)

        geometry_factor = float(np.cos(np.radians(abs(panel_tilt - max(10.0, abs(lat_val))))))
        geometry_factor = max(0.75, min(1.08, geometry_factor))

        # Interactive Dark-Matter Map (Plotly 7+ Scattermap)
        map_fig = go.Figure(
            go.Scattermap(
                lat=[lat_val],
                lon=[lon_val],
                mode="markers+text",
                marker=dict(size=13, color="#f59e0b"),
                text=[short_name],
                textposition="top right",
            )
        )
        map_fig.update_layout(
            map=dict(
                style="carto-darkmatter",
                center=dict(lat=lat_val, lon=lon_val),
                zoom=10.5,
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=215,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(map_fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        try:
            meteo_data = fetch_open_meteo_telemetry(lat_val, lon_val)
            tz_name = meteo_data.get("timezone", "UTC")
            current_block = meteo_data.get("current", {})
            hourly_block = meteo_data.get("hourly", {})
        except Exception as e:
            st.error(f"Telemetry stream interrupted: {e}")
            current_block, hourly_block, tz_name = {}, {}, "UTC"

        using_noon_sim = False
        eff_rad = float(current_block.get("shortwave_radiation", 0.0))
        eff_is_day = int(current_block.get("is_day", 0))
        eff_temp = float(current_block.get("temperature_2m", 25.0))
        eff_rh = float(current_block.get("relative_humidity_2m", 60.0))
        eff_cloud = float(current_block.get("cloud_cover", 10.0))
        eff_wind10 = float(current_block.get("wind_speed_10m", 5.0))
        eff_wdir10 = float(current_block.get("wind_direction_10m", 180.0))
        eff_pres = float(current_block.get("pressure_msl", 1013.0))
        eff_precip = float(current_block.get("precipitation", 0.0))
        eff_snow = float(current_block.get("snowfall", 0.0))
        eff_cl_low = float(current_block.get("cloud_cover_low", 0.0))
        eff_cl_mid = float(current_block.get("cloud_cover_mid", 0.0))
        eff_cl_high = float(current_block.get("cloud_cover_high", 0.0))
        eff_wind80 = float(current_block.get("wind_speed_80m", eff_wind10 * 1.2))
        eff_wdir80 = float(current_block.get("wind_direction_80m", eff_wdir10))
        eff_gust = float(current_block.get("wind_gusts_10m", eff_wind10 * 1.3))

        times_list = hourly_block.get("time", [])
        if sim_noon and times_list:
            noon_indices = [i for i, t in enumerate(times_list) if "T12:00" in t]
            if noon_indices:
                idx = noon_indices[0]
                using_noon_sim = True
                eff_rad = float(hourly_block["shortwave_radiation"][idx])
                eff_is_day = 1
                eff_temp = float(hourly_block["temperature_2m"][idx])
                eff_rh = float(hourly_block["relative_humidity_2m"][idx])
                eff_cloud = float(hourly_block["cloud_cover"][idx])
                eff_wind10 = float(hourly_block["wind_speed_10m"][idx])

        zen_now, az_now, aoi_now = compute_solar_angles(
            lat_val,
            lon_val,
            datetime.now(timezone.utc) if not using_noon_sim else datetime.now(timezone.utc).replace(hour=6, minute=30),
            panel_tilt=panel_tilt,
            panel_azimuth=panel_az,
        )

        active_telemetry = {
            "temperature_2_m_above_gnd": eff_temp,
            "relative_humidity_2_m_above_gnd": eff_rh,
            "mean_sea_level_pressure_MSL": eff_pres,
            "total_precipitation_sfc": eff_precip,
            "snowfall_amount_sfc": eff_snow,
            "total_cloud_cover_sfc": eff_cloud,
            "high_cloud_cover_high_cld_lay": eff_cl_high,
            "medium_cloud_cover_mid_cld_lay": eff_cl_mid,
            "low_cloud_cover_low_cld_lay": eff_cl_low,
            "shortwave_radiation_backwards_sfc": eff_rad,
            "wind_speed_10_m_above_gnd": eff_wind10,
            "wind_direction_10_m_above_gnd": eff_wdir10,
            "wind_speed_80_m_above_gnd": eff_wind80,
            "wind_direction_80_m_above_gnd": eff_wdir80,
            "wind_speed_900_mb": eff_wind80 * 1.05,
            "wind_direction_900_mb": eff_wdir80,
            "wind_gust_10_m_above_gnd": eff_gust,
            "angle_of_incidence": aoi_now,
            "zenith": zen_now,
            "azimuth": az_now,
        }

        pred_kw = predict_power_kw(active_telemetry, is_day=eff_is_day, geometry_scale=geometry_factor)

        status_class = "status-pill-day" if (eff_is_day == 1 and eff_rad > 5) else "status-pill-night"
        status_text = (
            "PEAK NOON SIMULATION (12:00 LOCAL)"
            if using_noon_sim
            else ("DAYTIME SOLAR FLUX ACTIVE" if (eff_is_day == 1 and eff_rad > 5) else "NIGHTTIME // ZERO IRRADIANCE")
        )

        dist_badge = f"{active_loc.get('dist_km', 0.0):.0f} km from base"
        st.markdown(
            f"""
        <div class="telemetry-bar">
            <div>
                <strong style="color:#f8fafc;">TARGET:</strong> {html.escape(short_name.upper())} ({dist_badge}) &nbsp;|&nbsp;
                <strong style="color:#f8fafc;">COORDS:</strong> {lat_val:.4f}&deg;N, {lon_val:.4f}&deg;E &nbsp;|&nbsp;
                <strong style="color:#f8fafc;">TZ:</strong> {html.escape(tz_name)}
            </div>
            <div class="{status_class}">{status_text}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 5 CalibSun Glassmorphic KPI Cards (Using HTML entities &deg; and &sup2; to prevent encoding glitches)
        st.markdown(
            f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-name">SOLAR IRRADIANCE</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2"/></svg>
                </div>
                <div class="kpi-value">{eff_rad:.1f}<span class="kpi-unit">W/m&sup2;</span></div>
                <div class="kpi-sub">AOI: {aoi_now:.1f}&deg; | Zenith: {zen_now:.1f}&deg;</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-name">AMBIENT TEMP</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>
                </div>
                <div class="kpi-value">{eff_temp:.1f}<span class="kpi-unit">&deg;C</span></div>
                <div class="kpi-sub">MSL Pressure: {eff_pres:.0f} hPa</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-name">REL. HUMIDITY</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
                </div>
                <div class="kpi-value">{eff_rh:.0f}<span class="kpi-unit">%</span></div>
                <div class="kpi-sub">Precip: {eff_precip:.1f} mm</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-name">CLOUD OPACITY</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>
                </div>
                <div class="kpi-value">{eff_cloud:.0f}<span class="kpi-unit">%</span></div>
                <div class="kpi-sub">L/M/H: {eff_cl_low:.0f}/{eff_cl_mid:.0f}/{eff_cl_high:.0f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-name">WIND VELOCITY</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2"/></svg>
                </div>
                <div class="kpi-value">{eff_wind10:.1f}<span class="kpi-unit">km/h</span></div>
                <div class="kpi-sub">80m Hub: {eff_wind80:.1f} km/h</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Primary Power Yield Output Card
        st.markdown(
            f"""
        <div class="yield-hero">
            <div>
                <div class="yield-eyebrow">ESTIMATED ACTIVE PHOTOVOLTAIC GENERATION</div>
                <div class="yield-location">{html.escape(short_name.upper())} // GRID DISPATCH ESTIMATE</div>
                <div class="yield-note">
                    Random Forest ensemble inference scaled by array tilt ({panel_tilt}&deg;) &amp; azimuth ({panel_az}&deg;).
                </div>
            </div>
            <div class="yield-number-box">
                <span class="yield-number">{pred_kw:,.2f}</span><span class="yield-unit">kW</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 48-Hour Meteosource-Style Spline Forecast Chart
        if times_list:
            df_48 = pd.DataFrame({"time": pd.to_datetime(times_list[:48])})
            preds_48 = []
            for i in range(min(48, len(times_list))):
                rad_i = float(hourly_block["shortwave_radiation"][i])
                is_d_i = int(hourly_block["is_day"][i])
                t_row = dict(active_telemetry)
                t_row["temperature_2_m_above_gnd"] = float(hourly_block["temperature_2m"][i])
                t_row["relative_humidity_2_m_above_gnd"] = float(hourly_block["relative_humidity_2m"][i])
                t_row["total_cloud_cover_sfc"] = float(hourly_block["cloud_cover"][i])
                t_row["shortwave_radiation_backwards_sfc"] = rad_i
                t_row["wind_speed_10_m_above_gnd"] = float(hourly_block["wind_speed_10m"][i])
                preds_48.append(predict_power_kw(t_row, is_day=is_d_i, geometry_scale=geometry_factor))

            df_48["power_kw"] = preds_48
            df_48["p90_upper"] = df_48["power_kw"] * 1.10
            df_48["p10_lower"] = df_48["power_kw"] * 0.90

            fig_48 = go.Figure()
            fig_48.add_trace(
                go.Scatter(
                    x=list(df_48["time"]) + list(df_48["time"])[::-1],
                    y=list(df_48["p90_upper"]) + list(df_48["p10_lower"])[::-1],
                    fill="toself",
                    fillcolor="rgba(14, 165, 233, 0.08)",
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    name="P10-P90 Uncertainty Band",
                )
            )
            fig_48.add_trace(
                go.Scatter(
                    x=df_48["time"],
                    y=df_48["power_kw"],
                    mode="lines",
                    name="Predicted PV Output (kW)",
                    line=dict(color="#f59e0b", width=2.6, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(245, 158, 11, 0.14)",
                    hovertemplate="<b>%{x|%a %H:%M}</b><br>Output: <b>%{y:,.1f} kW</b><extra></extra>",
                )
            )
            fig_48.update_layout(
                title=dict(
                    text="48-HOUR DIURNAL GENERATION PROFILE (15-MIN SPLINE INTERPOLATION)",
                    font=dict(family="JetBrains Mono, monospace", size=12, color="#94a3b8"),
                ),
                paper_bgcolor="rgba(11, 17, 30, 0.78)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(l=16, r=16, t=42, b=16),
                hovermode="x unified",
                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(148, 163, 184, 0.08)",
                    tickfont=dict(family="JetBrains Mono", size=11, color="#64748b"),
                ),
                yaxis=dict(
                    title="Power (kW)",
                    showgrid=True,
                    gridcolor="rgba(148, 163, 184, 0.08)",
                    tickfont=dict(family="JetBrains Mono", size=11, color="#64748b"),
                    zeroline=False,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=11, color="#94a3b8"),
                ),
            )
            st.plotly_chart(
                fig_48,
                use_container_width=True,
                config={"displaylogo": False, "toImageButtonOptions": {"format": "svg", "filename": "spgx_48h_forecast"}},
            )


# ------------------------------------------------------------------------------
# TAB 2: MANUAL TELEMETRY CONTROLS & FEATURE MATRIX
# ------------------------------------------------------------------------------
with tab_matrix:
    m_left, m_right = st.columns([2.2, 1.0], gap="large")

    manual_inputs = {}
    categories = [
        ("Solar Geometry & Flux", "IRRADIANCE & INCIDENCE VECTORS"),
        ("Atmospheric Cloud Layers", "THREE-TIER CLOUD OPACITY"),
        ("Surface Meteorology", "BOUNDARY LAYER THERMODYNAMICS"),
        ("Multi-Altitude Wind Profile", "ANEMOMETER & HUB SHEAR"),
    ]

    with m_left:
        for cat_name, cat_tag in categories:
            st.markdown(
                f"""
            <div class="corp-panel">
                <div class="panel-header">
                    <div class="panel-title">{html.escape(cat_name)}</div>
                    <span class="panel-tag">{html.escape(cat_tag)}</span>
                </div>
            """,
                unsafe_allow_html=True,
            )
            cat_items = [item for item in FEATURE_SCHEMA if item[4] == cat_name]
            cols = st.columns(3)
            for idx, (col_key, clean_label, unit_str, default_val, _) in enumerate(cat_items):
                with cols[idx % 3]:
                    manual_inputs[col_key] = st.number_input(
                        f"{clean_label} [{unit_str}]",
                        value=float(default_val),
                        step=0.5,
                        format="%.2f",
                        key=f"man_{col_key}",
                    )
            st.markdown("</div>", unsafe_allow_html=True)

    with m_right:
        man_pred_kw = predict_power_kw(manual_inputs, is_day=1)
        st.markdown(
            f"""
        <div class="yield-hero" style="flex-direction:column; align-items:flex-start;">
            <div class="yield-eyebrow">MANUAL TELEMETRY DISPATCH SIMULATION</div>
            <div class="yield-number" style="margin:0.5rem 0;">{man_pred_kw:,.2f}<span class="yield-unit">kW</span></div>
            <div class="yield-note">
                Real-time Random Forest response across all 20 atmospheric &amp; geometric parameters.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        oob_warnings = []
        for col_key, clean_label, unit_str, _, _ in FEATURE_SCHEMA:
            if col_key in feature_bounds:
                c_min, c_max, _ = feature_bounds[col_key]
                v = manual_inputs[col_key]
                if v < c_min or v > c_max:
                    oob_warnings.append(f"• **{clean_label}**: `{v:.1f} {unit_str}` outside training range (`{c_min:.1f}` – `{c_max:.1f}`)")

        st.markdown(
            """
        <div class="corp-panel">
            <div class="panel-header">
                <div class="panel-title">Model Domain Diagnostics</div>
                <span class="panel-tag">20 FEATURES</span>
            </div>
        """,
            unsafe_allow_html=True,
        )
        if oob_warnings:
            st.warning("Extrapolation detected on the following inputs:\n\n" + "\n".join(oob_warnings[:6]))
        else:
            st.success("All 20 manual inputs reside within historical training distribution bounds.")
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 3: NASA POWER HISTORICAL VALIDATION WORKBENCH
# ------------------------------------------------------------------------------
with tab_nasa:
    st.markdown(
        f"""
    <div class="telemetry-bar">
        <div>
            <strong style="color:#f8fafc;">NASA LARC POWER ARCHIVE //</strong>
            Validating most recent published 7-day satellite window for <strong>{html.escape(short_name.upper())}</strong> ({lat_val:.4f}&deg;N, {lon_val:.4f}&deg;E)
        </div>
        <span class="panel-tag">TIME STANDARD: UTC</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    try:
        df_nasa = fetch_nasa_power_recent(lat_val, lon_val)
    except Exception as e:
        st.error(f"NASA POWER archive request failed: {e}")
        df_nasa = pd.DataFrame()

    if not df_nasa.empty:
        peak_irr = df_nasa["irradiance_wm2"].max()
        peak_mod_kw = df_nasa["predicted_kw"].max()
        total_mwh = df_nasa["predicted_kw"].sum() / 1000.0

        st.markdown(
            f"""
        <div class="kpi-grid" style="grid-template-columns: repeat(3, 1fr);">
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">PEAK SATELLITE IRRADIANCE</span></div>
                <div class="kpi-value">{peak_irr:,.0f}<span class="kpi-unit">W/m&sup2;</span></div>
                <div class="kpi-sub">NASA ALLSKY_SFC_SW_DWN</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">PEAK MODEL OUTPUT</span></div>
                <div class="kpi-value">{peak_mod_kw:,.0f}<span class="kpi-unit">kW</span></div>
                <div class="kpi-sub">7-Day Maximum Dispatch</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top"><span class="kpi-name">CUMULATIVE 7-DAY YIELD</span></div>
                <div class="kpi-value">{total_mwh:,.1f}<span class="kpi-unit">MWh</span></div>
                <div class="kpi-sub">Integrated Hourly Generation</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        fig_nasa = go.Figure()
        fig_nasa.add_trace(
            go.Scatter(
                x=df_nasa["timestamp"],
                y=df_nasa["irradiance_wm2"],
                name="NASA Surface Irradiance (W/m2)",
                mode="lines",
                line=dict(color="#f59e0b", width=2.2, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(245, 158, 11, 0.12)",
            )
        )
        fig_nasa.add_trace(
            go.Scatter(
                x=df_nasa["timestamp"],
                y=df_nasa["predicted_kw"],
                name="Model Estimated Power (kW)",
                mode="lines",
                line=dict(color="#0ea5e9", width=2.2, shape="spline"),
                yaxis="y2",
            )
        )
        fig_nasa.update_layout(
            title=dict(
                text="7-DAY SATELLITE IRRADIANCE vs. RANDOM FOREST POWER RECONSTRUCTION",
                font=dict(family="JetBrains Mono, monospace", size=12, color="#94a3b8"),
            ),
            paper_bgcolor="rgba(11, 17, 30, 0.78)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            margin=dict(l=20, r=20, t=48, b=20),
            hovermode="x unified",
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(148, 163, 184, 0.08)",
                tickfont=dict(family="JetBrains Mono", size=11, color="#64748b"),
            ),
            yaxis=dict(
                title="Irradiance (W/m2)",
                showgrid=True,
                gridcolor="rgba(148, 163, 184, 0.08)",
                tickfont=dict(family="JetBrains Mono", size=11, color="#f59e0b"),
            ),
            yaxis2=dict(
                title="Model Output (kW)",
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(family="JetBrains Mono", size=11, color="#0ea5e9"),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11, color="#94a3b8"),
            ),
        )
        st.plotly_chart(fig_nasa, use_container_width=True, config={"displaylogo": False})

        csv_bytes = df_nasa.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export 7-Day NASA Validation Dataset (CSV)",
            data=csv_bytes,
            file_name=f"spgx_nasa_validation_{short_name.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No valid hourly records returned from NASA POWER for the selected window.")

# ==============================================================================
# 7. CORPORATE ARCHITECTURE & SUPPORTING APIs FOOTER DOCK
# ==============================================================================
st.markdown(
    """
<div class="arch-footer">
    <div class="api-strip-label">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
        SYSTEM INFRASTRUCTURE // SUPPORTING APIS &amp; TELEMETRY PIPELINES
    </div>
    <div class="arch-grid">
        <div class="arch-card">
            <div class="arch-role">METEOROLOGICAL FORECASTING</div>
            <div class="arch-provider">Open-Meteo Weather API</div>
            <div class="arch-desc">Real-time 15-minute &amp; hourly numerical weather prediction (NWP), multi-altitude wind shear (10m/80m), and shortwave radiation flux.</div>
        </div>
        <div class="arch-card">
            <div class="arch-role">SATELLITE VALIDATION</div>
            <div class="arch-provider">NASA LaRC POWER Archive</div>
            <div class="arch-desc">Prediction Of Worldwide Energy Resources (Agroclimatology &amp; Renewable Energy) surface shortwave downward irradiance (ALLSKY_SFC_SW_DWN).</div>
        </div>
        <div class="arch-card">
            <div class="arch-role">GEOSPATIAL &amp; GEOCODING</div>
            <div class="arch-provider">Google Maps / OSM Nominatim &amp; Photon</div>
            <div class="arch-desc">Multi-engine forward geocoding with Haversine proximity ranking, Indian PIN/substation resolution, and CARTO DarkMatter vector tiles.</div>
        </div>
        <div class="arch-card">
            <div class="arch-role">MACHINE LEARNING &amp; VISUALIZATION</div>
            <div class="arch-provider">Scikit-Learn RF &amp; Plotly WebGL</div>
            <div class="arch-desc">20-feature Random Forest regression ensemble paired with solar zenith/AOI geometry synthesis and spline-interpolated diurnal curves.</div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)