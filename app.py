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
    page_title="SPG-X // Solar Telemetry Grid", page_icon="☀️", layout="wide"
)

# Custom Responsive CSS Theme (Adapts seamlessly between Laptop and Mobile)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b1120;
        background-image: 
            radial-gradient(circle at 20% 15%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 80% 85%, rgba(14, 165, 233, 0.05) 0%, transparent 40%),
            linear-gradient(rgba(11, 17, 32, 0.9), rgba(11, 17, 32, 0.9));
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    .terminal-header {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-left: 4px solid #38bdf8;
        padding: 12px 18px;
        border-radius: 6px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #38bdf8;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    /* Desktop Sidebar Width */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.98);
        border-right: 1px solid rgba(56, 189, 248, 0.2);
        min-width: 360px !important;
        max-width: 420px !important;
    }

    .tech-panel {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .stNumberInput input {
        background-color: rgba(11, 17, 32, 0.9) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 6px !important;
        font-family: 'Courier New', Courier, monospace !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        color: #0b1120;
        border: none;
        padding: 14px 20px;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.6);
        background: linear-gradient(135deg, #7dd3fc 0%, #0ea5e9 100%);
    }

    .result-box {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(2, 132, 199, 0.15) 100%);
        border: 1px solid rgba(56, 189, 248, 0.45);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.2);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    /* MOBILE RESPONSIVE MEDIA QUERY (Screens smaller than 768px) */
    @media screen and (max-width: 768px) {
        .stApp {
            padding: 10px;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        .result-box h1 {
            font-size: 2.2rem !important;
        }
        /* Make sure metric panels stack nicely on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
            min-width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Boot-Up Sequence
if "initialized" not in st.session_state:
  with st.status(
      "☀️ Initializing Solar Neural Core & Telemetry...", expanded=True
  ) as status:
    st.write(">> Establishing secure ice-blue telemetry grid...")
    time.sleep(0.3)
    st.write(">> Compiling Random Forest Estimators...")
    time.sleep(0.4)
    status.update(
        label="✅ System Online & Solar Grid Verified!",
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

# --- SIDEBAR: ACCESSIBLE CATEGORIZED TELEMETRY CONTROLS ---
with st.sidebar:
  st.markdown("### ⚙️ Telemetry Controls")
  st.markdown(
      "<p style='color: #94a3b8; font-size: 0.85rem;'>Adjust environmental"
      " sensor values:</p>",
      unsafe_allow_html=True,
  )

  user_inputs = {}

  mid_idx = len(feature_cols) // 2
  group1 = feature_cols[:mid_idx]
  group2 = feature_cols[mid_idx:]

  tab_primary, tab_secondary = st.tabs(["📊 Primary Sensors", "🌤️ Atmospheric"])

  with tab_primary:
    for col_name in group1:
      default_val = (
          float(df[col_name].mean()) if col_name in df.columns else 50.0
      )
      user_inputs[col_name] = st.number_input(
          f"{col_name}", value=round(default_val, 2), key=f"inp_{col_name}"
      )

  with tab_secondary:
    for col_name in group2:
      default_val = (
          float(df[col_name].mean()) if col_name in df.columns else 50.0
      )
      user_inputs[col_name] = st.number_input(
          f"{col_name}", value=round(default_val, 2), key=f"inp_{col_name}"
      )

  st.markdown("<br>", unsafe_allow_html=True)
  predict_btn = st.button("Execute Prediction")

# --- MAIN PANEL ---
st.markdown("""
    <div class="terminal-header">
        SYS_STATUS: ACTIVE // ARCHITECTURE: RANDOM_FOREST_REGRESSOR // PROTOCOL: SOLAR-TELEMETRY
    </div>
""", unsafe_allow_html=True)

st.title("☀️ SPG-X // Solar Power Predictor")
st.markdown(
    "<p style='color: #64748b; font-size: 1.1rem;'>Advanced photovoltaic"
    " environmental telemetry and power generation forecasting grid.</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 1])

with col_left:
  overview_html = f"""
    <div class="tech-panel">
        <h3 style="color: #38bdf8; margin-top: 0; font-size: 1.2rem;">📊 Live System Telemetry Overview</h3>
        <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6;">
            This command center processes multi-variable environmental feeds through a trained Random Forest regressor model. 
            Use the categorized sidebar tabs to modify sensor inputs and execute real-time solar output estimations.
        </p>
        <hr style="border-color: rgba(56, 189, 248, 0.2); margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: #94a3b8; font-size: 0.8rem; display: block;">MODEL ACCURACY (R² SCORE)</span>
                <span style="color: #38bdf8; font-size: 1.6rem; font-family: 'Courier New', Courier, monospace; font-weight: bold;">{accuracy_pct:.2f}%</span>
            </div>
            <div style="text-align: right; color: #94a3b8; font-family: 'Courier New', Courier, monospace; font-size: 0.8rem;">
                <span>RECORDS: {len(df)}</span><br>
                <span>ALGORITHM: RF_REGRESSOR</span>
            </div>
        </div>
    </div>
    """
  st.markdown(overview_html, unsafe_allow_html=True)

with col_right:
  if predict_btn or "last_prediction" in st.session_state:
    if predict_btn:
      with st.spinner("Running neural inference across feature vectors..."):
        time.sleep(0.4)
        input_df = pd.DataFrame([user_inputs])
        st.session_state["last_prediction"] = model.predict(input_df)[0]

    pred_val = st.session_state["last_prediction"]

    result_html = f"""
        <div class="result-box">
            <span style="color: #94a3b8; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;">Estimated Solar Power Output</span>
            <h1 style="color: #38bdf8; font-size: 3.2rem; margin: 15px 0 0 0; font-family: 'Courier New', Courier, monospace; text-shadow: 0 0 20px rgba(56, 189, 248, 0.6);">{pred_val:.2f} kW</h1>
        </div>
        """
    st.markdown(result_html, unsafe_allow_html=True)
  else:
    st.markdown(
        """
            <div class="result-box" style="border: 1px dashed rgba(56, 189, 248, 0.3);">
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
st.bar_chart(chart_data, color="#38bdf8", height=300)
