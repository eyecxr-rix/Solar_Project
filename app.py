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
    "Dynamically generated input fields for every column in your `spg.csv`"
    " dataset."
)


@st.cache_resource
def load_data_and_train():
  csv_path = "spg.csv"

  if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    # Automatically treat all columns except the last one as features
    # and the last column as the target to predict
    feature_cols = list(df.columns[:-1])
    target_col = df.columns[-1]
    X = df[feature_cols]
    y = df[target_col]
  else:
    # Fallback if CSV isn't found yet
    feature_cols = ["Irradiation", "AmbientTemperature", "ModuleTemperature"]
    X = pd.DataFrame(
        np.random.uniform(100, 1000, size=(50, len(feature_cols))),
        columns=feature_cols,
    )
    y = X.iloc[:, 0] * 0.8

  model = RandomForestRegressor(n_estimators=50, random_state=42)
  model.fit(X, y)
  return model, feature_cols


try:
  model, feature_cols = load_data_and_train()
except Exception as e:
  st.error(f"Error loading dataset: {e}")
  st.stop()

# Create an input field for EVERY feature column found in spg.csv
st.subheader("Enter Values for All Dataset Conditions")
user_inputs = {}

# Display input boxes in two neat columns
cols = st.columns(2)
for i, col_name in enumerate(feature_cols):
  with cols[i % 2]:
    user_inputs[col_name] = st.number_input(f"{col_name}", value=0.0)

if st.button("Predict Power Generation", type="primary"):
  input_df = pd.DataFrame([user_inputs])
  prediction = model.predict(input_df)
  st.success(
      f"Estimated Power Generation: **{prediction[0]:.2f} kW**"
  )
