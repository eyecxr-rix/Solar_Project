import os
import pickle
import time
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

# Page configuration - WIDE LAYOUT for full screen utilization
st.set_page_config(
    page_title="SPG-X // Neural Telemetry", page_icon="⚡", layout="wide"
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
        padding: 12px 18px;
        border-radius: 6px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #00f0ff;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(8, 12, 24, 0.95);
        border-right: 1px solid rgba(0, 240, 255, 0.15);
    }

    /* Metric Cards / Tech Panels */
    .tech-panel {
        background: rgba(13, 20, 36, 0.65);
        border: 1px solid rgba(0, 240, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* Input Fields Styling */
    .stNumberInput input {
        background-color: rgba(5, 8, 20, 0.8) !important;
        color: #00f0ff !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 6px !important;
        font-family: 'Courier New', Courier, monospace !important;
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
    st.write(">> Parsing wide-screen telemetry layout matrices...")
    time.sleep(0.3)
    st.write(">> Compiling Random Forest Estimators...")
    time.sleep(0.4)
    status.update(
        label="✅ System Online & Wide-Screen Calibrated!",
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

# --- SIDEBAR: INPUT TELEMETRY PARAMETERS ---
with st.sidebar:
  st.markdown("### ⚙️ Telemetry Controls")
  st.markdown(
      "<p style='color: #64748b; font-size: 0.85rem;'>Adjust environmental"
      " sensor values:</p>",
      unsafe_allow_html=True,
  )

  user_inputs = {}
  for col_name in feature_cols:
    default_val = float(df[col_name].mean()) if col_name in df.columns else 50.0
    user_inputs[col_name] = st.number_input(
        f"{col_name}", value=round(default_val, 2)
    )

  st.markdown("<br>", unsafe_allow_html=True)
  predict_btn = st.button("Execute Prediction")

# --- MAIN PANEL: DASHBOARD & VISUALS ---
st.markdown("""
    <div class="terminal-header">
        SYS_STATUS: ACTIVE // ARCHITECTURE: WIDE_COMMAND_GRID // PROTOCOL: SPG-TELEMETRY
    </div>
""", unsafe_allow_html=True)

st.title("⚡ SPG-X // Neural Power Predictor")
st.markdown(
    "<p style='color: #64748b; font-size: 1.1rem;'>Advanced IoT environmental"
    " telemetry and power generation forecasting grid.</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# Layout columns for the main screen
col_left, col_right = st.columns([1.2, 1])

with col_left:
  st.markdown(
      """
        <div class="tech-panel">
            <h3 style="color: #00f0ff; margin-top: 0; font-size: 1.2rem;">📊 Live System Telemetry Overview</h3>
            <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
                This command center processes multi-variable environmental feeds through a trained Random Forest regressor model. 
                Use the sidebar controls to modify sensor inputs and execute real-time power generation estimations.
            </p>
            <hr style="border-color: rgba(0, 240, 255, 0.2); margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; color: #94a3b8; font-family: 'Courier New', Courier, monospace; font-size: 0.85rem;">
                <span>ACTIVE_MODEL: RandomForest</span>
                <span>DATA_POINTS: {}</span>
            </div>
        </div>
    """.format(
          len(df)
      ),
      unsafe_allow_html=True,
  )

with col_right:
  # Prediction execution logic
  if predict_btn or "last_prediction" in st.session_state:
    if predict_btn:
      with st.spinner("Running neural inference across feature vectors..."):
        time.sleep(0.4)
        input_df = pd.DataFrame([user_inputs])
        st.session_state["last_prediction"] = model.predict(input_df)[0]

    pred_val = st.session_state["last_prediction"]

    st.markdown(
        f"""
            <div class="result-box">
                <span style="color: #94a3b8; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;">Estimated Power Generation Output</span>
                <h1 style="color: #00f0ff; font-size: 3.2rem; margin: 15px 0 0 0; font-family: 'Courier New', Courier, monospace; text-shadow: 0 0 20px rgba(0, 240, 255, 0.6);">{pred_val:.2f} kW</h1>
            </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        """
            <div class="result-box" style="border: 1px dashed rgba(0, 240, 255, 0.3);">
                <span style="color: #64748b; font-size: 0.9rem;">Awaiting Telemetry Execution...</span>
                <p style="color: #64748b; font-size: 0.8rem; margin-top: 10px;">Click 'Execute Prediction' in the sidebar to calculate output.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Bottom Feature Distribution Chart Preview
st.markdown("### 📈 Real-Time Sensor Feature Distributions")
numeric_cols = df.select_dtypes(include=[np.number]).columns[:4]
st.line_chart(df[numeric_cols].head(50), height=250)
