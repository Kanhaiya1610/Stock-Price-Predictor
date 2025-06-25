from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='docs')

# Function to calculate RSI contribution (f(RSI))
def calculate_rsi_contribution(rsi):
    if 50 < rsi <= 70:
        return (rsi - 50) / 50
    elif 30 <= rsi < 50:
        return (rsi - 50) / -50
    return 0  # Neutral zone

# Function to calculate MACD contribution (g(MACD))
def calculate_macd_contribution(macd_histogram, macd_line, signal_line):
    return (macd_histogram + (macd_line - signal_line)) / 2

# Function to calculate Bollinger Bands contribution (h(Bollinger Bands))
def calculate_bollinger_bands_contribution(current_price, min_band, max_band):
    return (current_price - min_band) / (max_band - min_band) - 0.5

# Function to calculate predicted price change
def calculate_predicted_price_change(rsi, macd_histogram, macd_line, signal_line, current_price, min_band, max_band):
    f_rsi = calculate_rsi_contribution(rsi)
    g_macd = calculate_macd_contribution(macd_histogram, macd_line, signal_line)
    h_bollinger = calculate_bollinger_bands_contribution(current_price, min_band, max_band)

    alpha = 0.5  # RSI weight
    beta = 0.3   # MACD weight
    gamma = 0.2  # Bollinger Bands weight

    predicted_price_change = alpha * f_rsi + beta * g_macd + gamma * h_bollinger
    return predicted_price_change

# Function to calculate the predicted price
def calculate_predicted_price(current_price, predicted_price_change):
    return current_price * (1 + predicted_price_change / 100)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        rsi = float(data['rsi'])
        macd_histogram = float(data['macd_histogram'])
        macd_line = float(data['macd_line'])
        signal_line = float(data['signal_line'])
        current_price = float(data['current_price'])
        min_band = float(data['min_band'])
        max_band = float(data['max_band'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid input'}), 400

    predicted_price_change = calculate_predicted_price_change(
        rsi, macd_histogram, macd_line, signal_line, current_price, min_band, max_band
    )
    predicted_price = calculate_predicted_price(current_price, predicted_price_change)

    return jsonify({
        'predicted_price_change': round(predicted_price_change, 2),
        'predicted_price': round(predicted_price, 2)
    })

if __name__ == "__main__":
    app.run(debug=True)
