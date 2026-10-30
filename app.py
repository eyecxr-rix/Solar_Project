import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

# Page configuration
st.set_page_config(
    page_title="Solar Energy Predictor Pro", page_icon="☀️", layout="centered"
)

# Custom CSS for animations, gradients, and professional styling
st.markdown("""
    <style>
    /* Smooth fade-in animation for the whole app */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stApp {
        animation: fadeIn 0.6s ease-out;
    }

    /* Modern Card Container */
    .css-1r6slb0, .element-container {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Styled Predict Button with Hover Effect */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 69, 0, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 69, 0, 0.5);
        background: linear-gradient(135deg, #FFA500 0%, #FF6347 100%);
    }

    /* Success Result Card */
    .success-card {
        background: linear-gradient(135deg, rgba(46, 139, 87, 0.15) 0%, rgba(60, 179, 113, 0.25) 100%);
        border: 1px solid rgba(60, 179, 113, 0.4);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        animation: fadeIn 0.5s ease-in-out;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("☀️ Solar Power Generation Predictor")
st.markdown(
    "*Professional AI-powered forecasting dashboard analyzing all environmental"
    " conditions.*"
)
st.markdown("---")


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
  st.error(f"Error loading dataset: {e}")
  st.stop()

# Input Section inside a clean layout
st.subheader("⚙️ Environmental & Weather Parameters")
st.markdown("Adjust the values below based on your conditions:")

user_inputs = {}
cols = st.columns(2)

for i, col_name in enumerate(feature_cols):
  with cols[i % 2]:
    default_val = (
        float(df[col_name].mean()) if col_name in df.columns else 50.0
    )
    user_inputs[col_name] = st.number_input(
        f"**{col_name}**", value=round(default_val, 2)
    )

st.markdown("")
if st.button("🚀 Predict Power Generation", type="primary"):
  input_df = pd.DataFrame([user_inputs])
  prediction = model.predict(input_df)

  # Display sleek animated result card
  st.markdown(
      f"""
        <div class="success-card">
            <h3 style="color: #2E8B57; margin: 0;">Estimated Power Output</h3>
            <h1 style="color: #3CB371; margin: 10px 0 0 0;">{prediction[0]:.2f} kW</h1>
        </div>
    """,
      unsafe_allow_html=True,
  )
