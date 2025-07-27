# from flask import Flask, request, jsonify, send_from_directory
# import os

# app = Flask(__name__, static_folder='docs')

# # Function to calculate RSI contribution (f(RSI))
# def calculate_rsi_contribution(rsi):
#     if 50 < rsi <= 70:
#         return (rsi - 50) / 50
#     elif 30 <= rsi < 50:
#         return (rsi - 50) / -50
#     return 0  # Neutral zone

# # Function to calculate MACD contribution (g(MACD))
# def calculate_macd_contribution(macd_histogram, macd_line, signal_line):
#     return (macd_histogram + (macd_line - signal_line)) / 2

# # Function to calculate Bollinger Bands contribution (h(Bollinger Bands))
# def calculate_bollinger_bands_contribution(current_price, min_band, max_band):
#     return (current_price - min_band) / (max_band - min_band) - 0.5

# # Function to calculate predicted price change
# def calculate_predicted_price_change(rsi, macd_histogram, macd_line, signal_line, current_price, min_band, max_band):
#     f_rsi = calculate_rsi_contribution(rsi)
#     g_macd = calculate_macd_contribution(macd_histogram, macd_line, signal_line)
#     h_bollinger = calculate_bollinger_bands_contribution(current_price, min_band, max_band)

#     alpha = 0.5  # RSI weight
#     beta = 0.3   # MACD weight
#     gamma = 0.2  # Bollinger Bands weight

#     predicted_price_change = alpha * f_rsi + beta * g_macd + gamma * h_bollinger
#     return predicted_price_change

# # Function to calculate the predicted price
# def calculate_predicted_price(current_price, predicted_price_change):
#     return current_price * (1 + predicted_price_change / 100)

# @app.route('/')
# def serve_index():
#     return send_from_directory(app.static_folder, 'index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.json
#     try:
#         rsi = float(data['rsi'])
#         macd_histogram = float(data['macd_histogram'])
#         macd_line = float(data['macd_line'])
#         signal_line = float(data['signal_line'])
#         current_price = float(data['current_price'])
#         min_band = float(data['min_band'])
#         max_band = float(data['max_band'])
#     except (KeyError, ValueError):
#         return jsonify({'error': 'Invalid input'}), 400

#     predicted_price_change = calculate_predicted_price_change(
#         rsi, macd_histogram, macd_line, signal_line, current_price, min_band, max_band
#     )
#     predicted_price = calculate_predicted_price(current_price, predicted_price_change)

#     return jsonify({
#         'predicted_price_change': round(predicted_price_change, 2),
#         'predicted_price': round(predicted_price, 2)
#     })

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os
import json
from flask import jsonify, request
from werkzeug.utils import secure_filename # For secure file uploads
import google.generativeai as genai

app = Flask(__name__, static_folder='docs')

# --- Configure Gemini API ---

UPLOAD_FOLDER = 'uploads' # Create this folder in your project
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# It's best practice to set this as an environment variable
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
genai.configure(api_key="AIzaSyDs99bTEhiy-_iE_R6lFP7INaiW5IZcqEc") # Replace with your key

# --- Calculation Logic (Mirrors your JS logic) ---
# We can define the signal calculation functions here on the server
def calculate_rsi_signal(inputs):
    rsi = inputs['rsiValue']
    if rsi > 80: return -min(1, (rsi - 80) / 10)
    if rsi < 20: return min(1, (20 - rsi) / 10)
    # Note: Your JS has a different formula for the 50-80 and 20-50 range.
    # We will use it here for consistency. A simple linear model is also fine.
    if rsi > 50: return (rsi - 50) / -30.0 # Approximate your squared formula
    if rsi < 50: return (50 - rsi) / 30.0 # Approximate your squared formula
    return 0

def calculate_macd_signal(inputs):
    hist = inputs['macdLine'] - inputs['signalLine']
    return max(-1, min(1, hist / 2.0))

def calculate_bollinger_signal(inputs, current_price):
    lower, upper = inputs['bbLower'], inputs['bbUpper']
    if upper <= lower: return 0
    mid = (upper + lower) / 2
    range_val = upper - mid
    if range_val == 0: return 0
    position = (current_price - mid) / range_val
    return -max(-1, min(1, position))

# Map indicator keys to their calculation functions
INDICATOR_FUNCTIONS = {
    'rsi': calculate_rsi_signal,
    'macd': calculate_macd_signal,
    'bollinger': lambda inputs, price: calculate_bollinger_signal(inputs, price)
    # Add other indicator functions here (stochastic, ma_slope, etc.)
    # For now, we'll make them return 0 if not defined
}

def get_signal_label(signal):
    if signal > 0.7: return 'Strong Buy'
    if signal > 0.2: return 'Buy'
    if signal < -0.7: return 'Strong Sell'
    if signal < -0.2: return 'Sell'
    return 'Neutral'

# --- Gemini Narrative Function ---
def generate_prediction_narrative(contributions, final_signal):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Sort by impact (signal * weight)
    sorted_contributions = sorted(
        [c for c in contributions if c['weight'] > 0],
        key=lambda x: abs(x['signal'] * x['weight']),
        reverse=True
    )
    
    primary_driver = sorted_contributions[0] if sorted_contributions else None
    
    prompt = f"""
    You are a succinct financial analyst bot.
    Based on the following weighted technical indicator data, provide a brief, one-paragraph analysis explaining the final prediction.
    Do not give financial advice.

    Final Signal: {get_signal_label(final_signal)} ({final_signal:.2f})

    Key Indicators:
    """
    for c in sorted_contributions[:3]: # Show top 3 drivers
        prompt += f"- {c['name']}: Signal is {get_signal_label(c['signal'])} ({c['signal']:.2f}) with a weight of {c['weight']:.2f}\n"

    prompt += "\nAnalysis:"

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating narrative: {e}")
        return "AI analysis could not be generated due to an error."

# --- Main API Route ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# In stock_price.py

# ... (add this new route) ...

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    # --- 1. Get Text and Multiple Image Files ---
    article_text = request.form.get('text', '')
    image_files = request.files.getlist('images') # Use getlist for multiple files

    if not article_text and not image_files:
        return jsonify({'error': 'No text or images provided'}), 400

    # --- 2. Prepare the prompt contents (text and images) ---
    prompt_parts = [
        f"""
        You are an expert financial technical analyst. Your task is to analyze the provided text and chart image(s) to generate a market strategy.

        **Analysis Steps:**
        1.  **Analyze the Image(s):** Identify key chart patterns (e.g., Head and Shoulders, Double Top/Bottom, Triangles, Flags), support/resistance levels, trendlines, and candlestick patterns.
        2.  **Analyze the Text:** Determine the sentiment and key information from the text.
        3.  **Synthesize:** Combine the visual chart analysis with the text analysis to form a cohesive opinion.
        4.  **Formulate Strategy:** Based on your synthesis, determine the sentiment, implied strategy, provide brief advice, and suggest weights for the technical indicators. The sum of weights should be close to 1.0.

        **Provided Text:**
        ---
        {article_text if article_text else "No text provided. Rely solely on the image analysis."}
        ---

        **Final Output:**
        Respond ONLY with a valid JSON object with the following keys: "sentiment", "strategy", "advice", and "weights" (an object with keys: "rsi", "stochastic", "macd", "ma_slope", "bollinger", "obv").
        """
    ]

    # Process and add images to the prompt
    for image_file in image_files:
        if image_file and allowed_file(image_file.filename):
            # Read image bytes and determine MIME type
            img_bytes = image_file.read()
            mime_type = image_file.mimetype
            prompt_parts.append({"inline_data": {"data": img_bytes, "mime_type": mime_type}})

    # --- 3. Call the Multimodal AI Model ---
    try:
        # Use the more powerful multimodal model
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt_parts)
        raw_text = response.text

        clean_json_string = raw_text.strip().removeprefix('```json').removesuffix('```').strip()
        parsed_json = json.loads(clean_json_string)
        return jsonify(parsed_json)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to process AI response.'}), 500


# Make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

PLATFORM_CONTEXT = """
The platform is a "Quantitative Momentum & Reversal Simulator".
It uses the following technical indicators:
- RSI (Momentum): Measures if a stock is overbought or oversold.
- Stochastic Oscillator (Reversal): Similar to RSI, helps spot reversals.
- MACD (Trend): Shows the relationship between two moving averages, indicating trend direction.
- MA Slope (Calculus-based Trend): Directly measures the slope of a moving average to quantify trend speed.
- Bollinger Bands (Volatility Reversal): Bands widen with volatility. Prices hitting the bands might suggest a reversal.
- OBV (Volume Pressure): Tracks if volume is flowing in or out of a stock.
Users can adjust the "weight" of each indicator using a slider from 0 to 1. The weight determines how much influence that indicator has on the final prediction.
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('query', '')

    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # The prompt gives the AI its persona and context
    prompt = f"""
    You are "FinBot", a friendly and helpful AI assistant specializing in financial markets and this specific trading simulator.
    Your tone should be encouraging and educational. Do not give direct financial advice to buy or sell.

    Here is the context about the platform you are explaining:
    --- PLATFORM CONTEXT ---
    {PLATFORM_CONTEXT}
    --- END CONTEXT ---

    Now, answer the following user query based on your persona and the provided context.

    User Query: "{user_query}"

    Your Answer:
    """

    try:
        response = model.generate_content(prompt)
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    core_data = data['core']
    indicators_data = data['indicators']
    
    current_price = core_data['currentPrice']
    scaling_factor = core_data['scalingFactor']
    total_weight = core_data['totalWeight']

    combined_signal = 0
    contributions = []

    for key, values in indicators_data.items():
        weight = values['weight']
        if weight == 0:
            continue

        # Use a default function returning 0 if a specific one isn't mapped
        calc_func = INDICATOR_FUNCTIONS.get(key)
        signal = 0
        if calc_func:
            # Pass current price to functions that need it
            if key in ['bollinger', 'ma_slope']:
                 signal = calc_func(values['inputs'], current_price)
            else:
                 signal = calc_func(values['inputs'])

        combined_signal += signal * weight
        contributions.append({
            "name": key.replace("_", " ").title(), # Basic name from key
            "signal": signal,
            "weight": weight
        })

    if total_weight > 0:
        combined_signal /= total_weight
    else:
        combined_signal = 0

    # Calculate final price change (mirroring your JS)
    bb_data = indicators_data.get('bollinger', {}).get('inputs', {})
    bb_lower = bb_data.get('bbLower', current_price)
    bb_upper = bb_data.get('bbUpper', current_price)
    volatility = (bb_upper - bb_lower) / current_price if current_price > 0 else 0

    predicted_change_percentage = combined_signal * volatility * scaling_factor * 100
    predicted_change_value = current_price * (predicted_change_percentage / 100)
    predicted_price = current_price + predicted_change_value

    # Generate AI commentary
    explanation = generate_prediction_narrative(contributions, combined_signal)
    
    # Send all computed data back to the frontend
    return jsonify({
        'combined_signal': combined_signal,
        'predicted_price': round(predicted_price, 2),
        'predicted_change_value': round(predicted_change_value, 2),
        'predicted_change_percentage': round(predicted_change_percentage, 2),
        'explanation': explanation,
        'contributions': contributions
    })

if __name__ == "__main__":
    app.run(debug=True)