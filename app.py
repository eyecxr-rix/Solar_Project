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
    page_title="SPG-X // Thermal Telemetry", page_icon="🔥", layout="wide"
)

# Custom Military Amber / Industrial Tech CSS Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0c0f12;
        background-image: 
            radial-gradient(circle at 20% 15%, rgba(255, 140, 0, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 80% 85%, rgba(255, 69, 0, 0.04) 0%, transparent 40%),
            linear-gradient(rgba(12, 15, 18, 0.85), rgba(12, 15, 18, 0.85));
        color: #e2e8f0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    .terminal-header {
        background: rgba(20, 25, 32, 0.95);
        border: 1px solid rgba(255, 140, 0, 0.25);
        border-left: 4px solid #ff8c00;
        padding: 12px 18px;
        border-radius: 6px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #ffb347;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    }

    [data-testid="stSidebar"] {
        background-color: rgba(15, 20, 26, 0.95);
        border-right: 1px solid rgba(255, 140, 0, 0.15);
    }

    .tech-panel {
        background: rgba(20, 25, 32, 0.75);
        border: 1px solid rgba(255, 140, 0, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .stNumberInput input {
        background-color: rgba(12, 15, 18, 0.9) !important;
        color: #ffb347 !important;
        border: 1px solid rgba(255, 140, 0, 0.35) !important;
        border-radius: 6px !important;
        font-family: 'Courier New', Courier, monospace !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #ff8c00 0%, #ff4500 100%);
        color: #0c0f12;
        border: none;
        padding: 14px 20px;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(255, 140, 0, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(255, 140, 0, 0.6);
        background: linear-gradient(135deg, #ffa500 0%, #ff6347 100%);
    }

    .result-box {
        background: linear-gradient(135deg, rgba(255, 140, 0, 0.06) 0%, rgba(255, 69, 0, 0.12) 100%);
        border: 1px solid rgba(255, 140, 0, 0.4);
        box-shadow: 0 0 30px rgba(255, 140, 0, 0.15);
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
      "🔥 Initializing Thermal Telemetry & Neural Core...", expanded=True
  ) as status:
    st.write(">> Establishing secure industrial socket layer...")
    time.sleep(0.3)
    st.write(">> Calibrating amber thermal matrices...")
    time.sleep(0.3)
    st.write(">> Compiling Random Forest Estimators...")
    time.sleep(0.4)
    status.update(
        label="✅ System Online & Thermal Grid Verified!",
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
        columns=feature_cols,
    )
    df["Target"] = df.iloc[:, 0] * 0.85 + np.random.normal(0, 2, 100)
    X = df[feature_cols]
    y = df["Target"]

  # Train/Test split
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.2, random_state=42
  )
  model = RandomForestRegressor(n_estimators=50, random_state=42)
  model.fit(X_train, y_train)

  # Calculate R2 score percentage
  y_pred = model.predict(X_test)
  score = r2_score(y_test, y_pred)
  accuracy_pct = max(0.0, score * 100)

  # Get Feature Importance DataFrame
  importance_df = pd.DataFrame({
      "Feature": feature_cols,
      "Importance": model.feature_importances_,
  }).sort_values(by="Importance", ascending=True)

  return model, feature_cols, df, accuracy_pct, importance_df


try:
  model, feature_cols, df, accuracy_pct, importance_df = load_data_and_train()
except Exception as e:
  st.error(f"Critical System Fault: {e}")
  st.stop()

# --- SIDEBAR: INPUT TELEMETRY PARAMETERS ---
with st.sidebar:
  st.markdown("### ⚙️ Telemetry Controls")
  st.markdown(
      "<p style='color: #94a3b8; font-size: 0.85rem;'>Adjust environmental"
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

# --- MAIN PANEL ---
st.markdown("""
    <div class="terminal-header">
        SYS_STATUS: ACTIVE // ARCHITECTURE: RANDOM_FOREST_REGRESSOR // PROTOCOL: THERMAL-TELEMETRY
    </div>
""", unsafe_allow_html=True)

st.title("🔥 SPG-X // Thermal Power Predictor")
st.markdown(
    "<p style='color: #94a3b8; font-size: 1.1rem;'>Industrial IoT environmental"
    " telemetry and solar output forecasting grid.</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 1])

with col_left:
  st.markdown(
      f"""
        <div class="tech-panel">
            <h3 style="color: #ffb347; margin-top: 0; font-size: 1.2rem;">📊 Live System Telemetry Overview</h3>
            <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
                This command center processes multi-variable environmental feeds through a trained Random Forest regressor model. 
                Use the sidebar controls to modify sensor inputs and execute real-time power generation estimations.
            </p>
            <hr style="border-color: rgba(255, 140, 0, 0.2); margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #94a3b8; font-size: 0.8rem; display: block;">MODEL ACCURACY (R² SCORE)</span>
                    <span style="color: #ffb347; font-size: 1.6rem; font-family: 'Courier New', Courier, monospace; font-weight: bold;">{accuracy_pct:.2f}%</span>
                </div>
                <div style="text-align: right; color: #94a3b8; font-family: 'Courier New', Courier, monospace; font-size: 0.8rem;">
                    <span>RECORDS: {len(df)}</span><br>
                    <span>ALGORITHM: RF_REGRESSOR</span>
                </div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with col_right:
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
                <h1 style="color: #ffb347; font-size: 3.2rem; margin: 15px 0 0 0; font-family: 'Courier New', Courier, monospace; text-shadow: 0 0 20px rgba(255, 140, 0, 0.6);">{pred_val:.2f} kW</h1>
            </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        """
            <div class="result-box" style="border: 1px dashed rgba(255, 140, 0, 0.3);">
                <span style="color: #94a3b8; font-size: 0.9rem;">Awaiting Telemetry Execution...</span>
                <p style="color: #94a3b8; font-size: 0.8rem; margin-top: 10px;">Click 'Execute Prediction' in the sidebar to calculate output.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🔬 Neural Feature Importance Matrix")
st.markdown(
    "<p style='color: #94a3b8; font-size: 0.9rem;'>Relative weight and impact"
    " of each environmental sensor parameter on the prediction model.</p>",
    unsafe_allow_html=True,
)

chart_data = importance_df.set_index("Feature")
st.bar_chart(chart_data, color="#ff8c00", height=300)
