import os
import pickle
import time
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

# Page configuration - WIDE LAYOUT
st.set_page_config(
    page_title="SPG-X // Neural Telemetry", page_icon="⚡", layout="wide"
)

# Custom High-Tech Cyberpunk / Engineering CSS Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #050814;
        background-image: 
            radial-gradient(circle at 20% 15%, rgba(0, 240, 255, 0.07) 0%, transparent 40%),
            radial-gradient(circle at 80% 85%, rgba(255, 107, 0, 0.06) 0%, transparent 40%),
            linear-gradient(rgba(5, 8, 20, 0.8), rgba(5, 8, 20, 0.8));
        color: #cfd8dc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    .terminal-header {
        background: rgba(13, 20, 36, 0.9);
        border: 1px solid rgba(0, 240, 255, 0.2);
        border-left: 4px solid #00f0ff;
        padding: 12px 18px;
        border-radius: 6px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #00f0ff;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stSidebar"] {
        background-color: rgba(8, 12, 24, 0.95);
        border-right: 1px solid rgba(0, 240, 255, 0.15);
    }

    .tech-panel {
        background: rgba(13, 20, 36, 0.65);
        border: 1px solid rgba(0, 240, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .stNumberInput input {
        background-color: rgba(5, 8, 20, 0.8) !important;
        color: #00f0ff !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 6px !important;
        font-family: 'Courier New', Courier, monospace !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #00f0ff 0%, #0077ff 100%);
        color: #050814;
        border: none;
        padding: 14px 20px;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.7);
        background: linear-gradient(135deg, #33f3ff 0%, #1a8cff 100%);
    }

    .result-box {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.05) 0%, rgba(0, 119, 255, 0.1) 100%);
        border: 1px solid rgba(0, 240, 255, 0.4);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.15);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)

# Boot-Up Sequence
if "initialized" not in st.session_state:
  with st.status(
      "⚡ Initializing SPG-X Neural Core & Telemetry...", expanded=True
  ) as status:
    st.write(">> Establishing secure socket layer [SSL]...")
    time.sleep(0.3)
    st.write(">> Analyzing feature weights & importance matrices...")
    time.sleep(0.3)
    st.write(">> Compiling Random Forest Estimators...")
    time.sleep(0.4)
    status.update(
        label="✅ System Online & Feature Weights Verified!",
        state="complete",
        expanded=False,
    )
  st.session_state["initialized"] = True


@st.cache_resource
def load_data_and_train():
  csv_path = "spg.csv"

  if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    feature_cols = list(df.columns[:-1])
    target_col = df.columns[-1]
    X = df[feature_cols]
    y = df[target_col]
  else:
    feature_cols = ["Irradiation", "AmbientTemperature", "ModuleTemperature"]
    df = pd.DataFrame(
        np.random.uniform(100, 1000, size=(100, len(feature_cols))),
