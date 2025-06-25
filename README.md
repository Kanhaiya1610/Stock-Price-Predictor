# Stock Price Predictor

A modern, interactive, and educational dashboard for simulating stock price predictions using multiple technical indicators, customizable weights, and advanced analytics.  
**Built with Python (Flask) backend and a beautiful TailwindCSS-powered frontend.**

---

## 🚀 Features

- **Multiple Indicators:** RSI, Stochastic, MACD, MA Slope, Bollinger Bands, OBV
- **Customizable Weights:** User can set the importance of each indicator
- **Preset Strategies:** Momentum, Mean Reversion, Balanced, or Custom
- **Live Combined Signal Gauge:** Visual needle for overall market signal
- **AI-style Analyst Commentary:** Explains the main drivers of the prediction
- **Export/Save:** Download your settings and results as a JSON file
- **Modern UI:** Responsive, dark mode, and mobile-friendly
- **No real money or live trading – for educational/demo use only**

---

## 🖥️ Demo

![Dashboard Screenshot](screenshot.png) <!-- Add a screenshot if you want -->

---

## 🛠️ Setup Guide

### 1. **Clone the Repository**
```sh
git clone https://github.com/Kanhaiya1610/Stock-Price-Predictor.git
cd Stock-Price-Predictor
```

### 2. **Install Python Dependencies**
Make sure you have Python 3.7+ and pip installed.
```sh
pip install -r requirements.txt
```

### 3. **Run the Flask Server**
```sh
python stock_price.py
```
By default, the app runs at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

### 4. **Open the Dashboard**
Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📋 User Manual

### **Dashboard Sections**

- **Core Market Data:**  
  - Enter the current stock price and adjust prediction sensitivity.

- **Preset Strategy:**  
  - Choose from Momentum, Mean Reversion, Balanced, or Custom to auto-set indicator weights.

- **Indicators:**  
  - Adjust values and weights for RSI, Stochastic, MACD, MA Slope, Bollinger Bands, and OBV.
  - Each indicator shows its own signal (Strong Buy, Buy, Neutral, Sell, Strong Sell).

- **Combined Signal Gauge:**  
  - Visual needle shows the overall market signal based on your settings.

- **Prediction Output:**  
  - See the predicted price change (₹ and %) and the final predicted price.

- **AI Analyst Commentary:**  
  - Get a plain-English explanation of the prediction and its main drivers.

- **Indicator Contributions:**  
  - See how much each indicator is contributing to the final signal.

- **Export/Save:**  
  - Click "Export Settings & Result" to download your current setup and prediction as a JSON file.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change or add.

---

## 🐞 Issues

If you find a bug or want to request a feature, please open an [issue](https://github.com/Kanhaiya1610/Stock-Price-Predictor/issues).

---

## 📄 License

This project is licensed under the MIT License.

---

## ⚠️ Disclaimer

This tool is for educational and illustrative purposes only and does **not** constitute financial advice.  
No mathematical model can predict the market with certainty. Use at your own risk.

--- 