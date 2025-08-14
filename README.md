# Digital-Twin-Farm-
An interactive prototype that acts as a farm’s “digital brain” — simulating soil conditions, forecasting moisture levels, and guiding farmers on optimal irrigation timing for smarter, more efficient farming.
# 🌱 Farm Digital Twin — Soil Moisture Forecasting

A simple Digital Twin prototype for farms using **Python**, **Streamlit**, and **LSTM** to simulate, predict, and visualize soil moisture.

## 📂 Files
- `step1_data.py` → Generates synthetic soil moisture data.
- `soil_moisture.csv` → Generated dataset.
- `step2_lstm.py` → Trains LSTM model & forecasts moisture.
- `app.py` → Streamlit dashboard.

## ⚙️ How It Works
1. **Data Generation** – Simulates hourly soil moisture readings with random variations.
2. **Forecasting (LSTM)** – Predicts moisture for 6–24 hours ahead.
3. **Dashboard** – Shows current levels, forecasts, and irrigation advice.

## 🚀 Run It
```bash
pip install pandas matplotlib streamlit tensorflow
python step1_data.py
python step2_lstm.py
streamlit run app.py
