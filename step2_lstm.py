import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import joblib

# 1. Load data
data = pd.read_csv("soil_moisture.csv", parse_dates=["timestamp"], index_col="timestamp")

# 2. Prepare features
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# Save scaler for later use in app.py
joblib.dump(scaler, "scaler.pkl")

# 3. Create sequences for LSTM
def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

SEQ_LENGTH = 24  # past 24 hours
X, y = create_sequences(data_scaled, SEQ_LENGTH)

# 4. Train-test split
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# 5. Build LSTM model
model = Sequential()
model.add(LSTM(50, activation="relu", input_shape=(SEQ_LENGTH, 1)))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

# 6. Train model
model.fit(X_train, y_train, epochs=20, batch_size=16, validation_data=(X_test, y_test))

# 7. Save model
model.save("lstm_model.h5")

# 8. Forecast next 24 hours
last_seq = data_scaled[-SEQ_LENGTH:]
predictions_scaled = []

current_seq = last_seq.reshape(1, SEQ_LENGTH, 1)
for _ in range(24):
    pred = model.predict(current_seq, verbose=0)
    predictions_scaled.append(pred[0][0])
    current_seq = np.append(current_seq[:, 1:, :], [[pred]], axis=1)

# 9. Inverse transform predictions
predictions = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1))

# 10. Save predictions to CSV
future_index = pd.date_range(start=data.index[-1] + pd.Timedelta(hours=1), periods=24, freq="h")
forecast_df = pd.DataFrame(predictions, index=future_index, columns=["predicted_soil_moisture"])
forecast_df.to_csv("soil_moisture_forecast.csv")

print("✅ LSTM model trained and predictions saved to soil_moisture_forecast.csv")
