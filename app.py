import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

# Page configuration
st.set_page_config(
    page_title="Solar Energy Predictor", page_icon="☀️", layout="centered"
)

st.title("☀️ Solar Power Generation Predictor")
st.write(
    "Predict solar power output based on environmental and weather conditions."
)


@st.cache_resource
def get_trained_model():
  model_path = "solar_model.pkl"

  # Train if model doesn't exist or is corrupted/empty
  train_needed = not os.path.exists(model_path)
  if not train_needed:
    try:
      with open(model_path, "rb") as f:
        return pickle.load(f)
    except Exception:
      train_needed = True

  if train_needed:
    # Generate robust synthetic training data to ensure zero dependency issues
    np.random.seed(42)
    X = pd.DataFrame({
        "Irradiation": np.random.uniform(100, 1000, 200),
        "AmbientTemperature": np.random.uniform(10, 45, 200),
        "ModuleTemperature": np.random.uniform(15, 75, 200),
    })
    y = X["Irradiation"] * 0.85 + np.random.normal(0, 3, 200)

    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    with open(model_path, "wb") as f:
      pickle.dump(model, f)

  with open(model_path, "rb") as f:
    return pickle.load(f)


# Load model safely
try:
  model = get_trained_model()
except Exception as e:
  st.error(f"Error initializing model: {e}")
  st.stop()

# Input form for user parameters
st.subheader("Enter Weather Parameters")
col1, col2 = st.columns(2)

with col1:
  radiation = st.number_input(
      "Irradiation / Solar Radiation", min_value=0.0, value=500.0
  )
  ambient_temp = st.number_input(
      "Ambient Temperature (°C)", min_value=-10.0, max_value=60.0, value=25.0
  )

with col2:
  module_temp = st.number_input(
      "Module Temperature (°C)", min_value=-10.0, max_value=90.0, value=30.0
  )

if st.button("Predict Power Generation", type="primary"):
  input_data = pd.DataFrame([[radiation, ambient_temp, module_temp]], columns=[
      "Irradiation",
      "AmbientTemperature",
      "ModuleTemperature",
  ])

  prediction = model.predict(input_data)
  st.success(
      f"Estimated Power Generation: **{prediction[0]:.2f} kW**"
  )
