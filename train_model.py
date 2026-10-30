import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

# 1. Load dataset
print("Loading dataset...")
df = pd.read_csv('spg.csv')
df = df.dropna()

# 2. Define features (X) and target (y)
X = df.drop(columns=['generated_power_kw'])
y = df['generated_power_kw']

# 3. Split into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train a Random Forest Regressor model
print("Training Random Forest model...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluate Performance
y_pred = model.predict(X_test)
score = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n--- Model Performance ---")
print(f"Random Forest R^2 Score: {score:.4f} (~{score*100:.1f}%)")
print(f"Root Mean Squared Error: {rmse:.2f} kW\n")

# 6. Feature Importance Analysis
print("--- Top Weather Features Driving Solar Power ---")
importances = model.feature_importances_
feature_importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
print(feature_importance_df.to_string(index=False))
print("\n")

# 7. Save the trained model explicitly in the current working directory
model_filename = 'solar_model.pkl'
joblib.dump(model, model_filename)
absolute_path = os.path.abspath(model_filename)
print(f"SUCCESS: Model saved at -> {absolute_path}\n")

# 8. Plotting Actual vs. Predicted Results
print("Generating evaluation plot...")
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.4, color='darkorange', edgecolor='k')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Perfect Prediction')
plt.xlabel('Actual Power Generated (kW)', fontsize=12)
plt.ylabel('Predicted Power Generated (kW)', fontsize=12)
plt.title('Actual vs. Predicted Solar Power Generation', fontsize=14)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()