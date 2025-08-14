# app.py
import time
import random
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# -----------------------
# SETTINGS (edit these)
# -----------------------
API_KEY = "dfba274b3e571535fdefe33dc69bc0e7"   # <-- your OpenWeather key
CITY = "Ludhiana"                              # <-- change if you want
OPENWEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

IRRIGATION_THRESHOLD = 30.0   # soil moisture % below which irrigation is considered
MIN_RAIN_FOR_NO_IRRIGATION = 2.0  # mm in last 1h considered enough to skip irrigation

# -----------------------
# FarmDigitalTwin class
# -----------------------
class FarmDigitalTwin:
    def __init__(self):
        self.data = pd.DataFrame(columns=["Time", "SoilMoisture", "Temperature", "Humidity", "Rainfall", "IrrigationApplied"])
        # basic stats for demo
        self.total_irrigations = 0

    def get_weather_data(self):
        """Get temperature, humidity, rainfall from OpenWeather; fallback to simulated on error"""
        try:
            r = requests.get(OPENWEATHER_URL, timeout=5)
            r.raise_for_status()
            w = r.json()
            temp = float(w["main"]["temp"])
            humidity = float(w["main"]["humidity"])
            rainfall = float(w.get("rain", {}).get("1h", 0))
            return temp, humidity, rainfall
        except Exception as e:
            # fallback: simulated weather
            temp = random.uniform(15, 35)
            humidity = random.uniform(30, 90)
            rainfall = random.uniform(0, 5)
            st.warning(f"OpenWeather fetch failed — using simulated weather. ({e})")
            return temp, humidity, rainfall

    def simulate_soil_moisture(self):
        """Very simple simulation of current soil moisture (for prototype)."""
        return random.uniform(10, 80)

    def add_reading(self, irrigation_applied=False):
        """Fetch one full reading and append to dataframe"""
        soil = self.simulate_soil_moisture()
        temp, hum, rain = self.get_weather_data()
        now = pd.Timestamp.now()
        row = {
            "Time": now,
            "SoilMoisture": round(soil, 2),
            "Temperature": round(temp, 2),
            "Humidity": round(hum, 2),
            "Rainfall": round(rain, 2),
            "IrrigationApplied": bool(irrigation_applied)
        }
        self.data = pd.concat([self.data, pd.DataFrame([row])], ignore_index=True)
        if irrigation_applied:
            self.total_irrigations += 1
        return row

    def check_irrigation_need(self, soil_moisture, rainfall):
        """Decision rule: water if soil < threshold and rainfall < MIN_RAIN..."""
        if soil_moisture < IRRIGATION_THRESHOLD and rainfall < MIN_RAIN_FOR_NO_IRRIGATION:
            return True
        return False

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Farm Digital Twin Prototype", layout="wide")
st.title("🌾 Farm Digital Twin — Prototype")

# store twin in session state so it persists across interactions
if "twin" not in st.session_state:
    st.session_state.twin = FarmDigitalTwin()

twin: FarmDigitalTwin = st.session_state.twin

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    st.write("City (OpenWeather):")
    city_input = st.text_input("City", CITY)
    if city_input != CITY:
        # update URL if city changed
        CITY = city_input
        OPENWEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        st.info(f"City changed to {CITY} — click 'Fetch Now' to get latest reading.")
    st.write("---")
    if st.button("Fetch Now"):
        row = twin.add_reading()
        st.success(f"Fetched reading @ {row['Time'].strftime('%H:%M:%S')}")
    st.write("Simulate multiple readings:")
    num_sim = st.number_input("Count", min_value=1, max_value=100, value=5, step=1)
    if st.button("Simulate"):
        progress = st.progress(0)
        for i in range(int(num_sim)):
            twin.add_reading()
            progress.progress((i+1)/int(num_sim))
            time.sleep(0.4)
        st.success(f"Simulated {num_sim} readings.")
    st.write("---")
    st.write("Irrigation control")
    if st.button("Apply Irrigation Now"):
        # Simple action: append reading and mark irrigation applied
        row = twin.add_reading(irrigation_applied=True)
        st.success(f"Irrigation applied @ {row['Time'].strftime('%Y-%m-%d %H:%M:%S')}")
    st.write("---")
    st.write("Quick tips")
    st.info("Use 'Fetch Now' to get current weather + simulated soil. Use 'Simulate' to generate history for charts.")

# Main layout: metrics + charts + table
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Current status")
    if not twin.data.empty:
        latest = twin.data.iloc[-1]
        st.metric("Soil Moisture (%)", f"{latest.SoilMoisture}")
        st.metric("Temperature (°C)", f"{latest.Temperature}")
        st.metric("Humidity (%)", f"{latest.Humidity}")
        st.metric("Rainfall (mm, last 1h)", f"{latest.Rainfall}")
        need = twin.check_irrigation_need(latest.SoilMoisture, latest.Rainfall)
        if need:
            st.error("Irrigation recommended now ⚠️")
        else:
            st.success("No irrigation needed ✅")
    else:
        st.write("No readings yet. Click **Fetch Now** or **Simulate** to start.")

    st.write("---")
    st.write(f"Total irrigation actions (this session): **{twin.total_irrigations}**")

with col2:
    st.subheader("Soil Moisture Trend")
    if not twin.data.empty:
        df = twin.data.copy()
        df["TimeStr"] = df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        fig = px.line(df, x="Time", y="SoilMoisture", markers=True, title=f"Soil Moisture over time ({CITY})")
        fig.add_hline(y=IRRIGATION_THRESHOLD, line_dash="dash", annotation_text="Irrigation threshold")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to plot yet.")

st.write("---")
st.subheader("Raw Data / History")
st.dataframe(twin.data.sort_values(by="Time", ascending=False).reset_index(drop=True))

st.write("---")
st.subheader("Decision log / last action")
if not twin.data.empty:
    last = twin.data.iloc[-1]
    st.write(f"Last reading at **{last['Time']}** — Soil {last['SoilMoisture']}% | Rain {last['Rainfall']}mm")
    if twin.check_irrigation_need(last.SoilMoisture, last.Rainfall):
        st.warning("Decision engine: Irrigation recommended. (You can click 'Apply Irrigation Now' in the sidebar.)")
    else:
        st.success("Decision engine: No irrigation needed.")

