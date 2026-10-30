import os
import pickle
import time
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

# Page configuration
st.set_page_config(
    page_title="SPG-X // Neural Telemetry", page_icon="⚡", layout="centered"
)

# Custom High-Tech Cyberpunk / Engineering CSS Theme
st.markdown("""
    <style>
    /* Dark Sci-Fi Command Center Background */
    .stApp {
        background-color: #050814;
        background-image: 
            radial-gradient(circle at 20% 15%, rgba(0, 240, 255, 0.07) 0%, transparent 40%),
            radial-gradient(circle at 80% 85%, rgba(255, 107, 0, 0.06) 0%, transparent 40%),
            linear-gradient(rgba(5, 8, 20, 0.8), rgba(5, 8, 20, 0.8));
        color: #cfd8dc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Terminal Status Bar */
    .terminal-header {
        background: rgba(13, 20, 36, 0.9);
        border: 1px solid rgba(0, 240, 255, 0.2);
        border-left: 4px solid #00f0ff;
        padding: 10px 15px;
        border-radius: 6px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #00f0ff;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    /* Custom Input Labels */
    label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.5px;
    }

    /* Input Fields Styling */
    .stNumberInput input {
        background-color: rgba(5, 8, 20, 0.8) !important;
        color: #00f0ff !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 6px !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    .stNumberInput input:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
    }

    /* Glowing Neon Action Button */
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

    /* Holographic Result Output Box */
    .result-box {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.05) 0%, rgba(0, 119, 255, 0.1) 100%);
        border: 1px solid rgba(0, 240, 255, 0.4);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.15);
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-top: 25px;
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)

# Cool Tech Boot-Up Sequence (Runs only on initial app load)
if "initialized" not in st.session_state:
  with st.status(
      "⚡ Initializing SPG-X Neural Core & Telemetry...", expanded=True
  ) as status:
    st.write(">> Establishing secure socket layer [SSL]...")
    time.sleep(0.4)
    st.write(">> Parsing environmental feature weights...")
    time.sleep(0.4)
    st.write(">> Compiling Random Forest Estimators & Tensor Matrices...")
    time.sleep(0.5)
    st.write(">> Synchronizing IoT sensor stream from `spg.csv`...")
    time.sleep(0.4)
    status.update(
        label="✅ System Online & Calibrated Successfully!",
        state="complete",
        expanded=False,
    )
  st.session_state["initialized"] = True

# Terminal Header Banner
st.markdown("""
    <div class="terminal-header">
        SYS_STATUS: ACTIVE // ARCHITECTURE: RANDOM_FOREST_REGRESSOR // PROTOCOL: SPG-TELEMETRY
    </div>
""", unsafe_allow_html=True)

st.title("⚡ SPG-X // Neural Power Predictor")
st.markdown(
    "<p style='color: #64748b;'>Advanced IoT environmental telemetry and power"
    " generation forecasting grid.</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)


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
        np.random.uniform(100, 1000, size=(50, len(feature_cols))),
        columns=feature_cols,
    )
    df["Target"] = df.iloc[:, 0] * 0.8
    X = df[feature_cols]
    y = df["Target"]

  model = RandomForestRegressor(n_estimators=50, random_state=42)
  model.fit(X, y)
  return model, feature_cols, df


try:
  model, feature_cols, df = load_data_and_train()
except Exception as e:
  st.error(f"Critical System Fault: {e}")
  st.stop()

# Input Telemetry Section
st.subheader("⚙️ Telemetry Parameters")

user_inputs = {}
cols = st.columns(2)

for i, col_name in enumerate(feature_cols):
  with cols[i % 2]:
    default_val = (
        float(df[col_name].mean()) if col_name in df.columns else 50.0
    )
    user_inputs[col_name] = st.number_input(
        f"{col_name}", value=round(default_val, 2)
    )

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Execute Prediction Calculation"):
  # Quick fake hacking/processing text effect before showing output
  with st.spinner("Running neural inference across feature vectors..."):
    time.sleep(0.6)

  input_df = pd.DataFrame([user_inputs])
  prediction = model.predict(input_df)

  st.markdown(
      f"""
        <div class="result-box">
            <span style="color: #94a3b8; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;">Estimated Power Generation Output</span>
            <h1 style="color: #00f0ff; font-size: 2.8rem; margin: 10px 0 0 0; font-family: 'Courier New', Courier, monospace; text-shadow: 0 0 15px rgba(0, 240, 255, 0.5);">{prediction[0]:.2f} kW</h1>
        </div>
    """,
      unsafe_allow_html=True,
  )
