import os
import pickle
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Solar Energy Predictor", page_icon="☀️", layout="centered"
)

st.title("☀️ Solar Power Generation Predictor")
st.write(
    "Predict solar power output based on environmental and weather conditions."
)

# Automatically generate or load the model
model_path = "solar_model.pkl"
if not os.path.exists(model_path):
  st.info(
      "Model file not found. Running training script to generate solar_model.pkl"
      " automatically..."
  )
  import train_model  # Runs the training script to create the pkl file

# Load the trained model
with open(model_path, "rb") as f:
  model = pickle.load(f)

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
  # Prepare input dataframe matching your training feature structure
  input_data = pd.DataFrame([[radiation, ambient_temp, module_temp]], columns=[
      "Irradiation",
      "AmbientTemperature",
      "ModuleTemperature",
  ])

  prediction = model.predict(input_data)
  st.success(
      f"Estimated Power Generation: **{prediction[0]:.2f} kW**"
  )