# step1_data.py
import numpy as np
import pandas as pd

# Simulate 30 days of hourly soil moisture data (0 to 100%)
hours = 24 * 30
time_index = pd.date_range(start="2025-07-01", periods=hours, freq="H")
soil_moisture = 40 + 10 * np.sin(np.linspace(0, 12*np.pi, hours)) + np.random.normal(0, 2, hours)

df = pd.DataFrame({"timestamp": time_index, "soil_moisture": soil_moisture})
df.to_csv("soil_moisture.csv", index=False)

print("Sample data saved to soil_moisture.csv")
