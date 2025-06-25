document.getElementById('prediction-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const rsi = document.getElementById('rsi').value;
    const macd_histogram = document.getElementById('macd_histogram').value;
    const macd_line = document.getElementById('macd_line').value;
    const signal_line = document.getElementById('signal_line').value;
    const current_price = document.getElementById('current_price').value;
    const min_band = document.getElementById('min_band').value;
    const max_band = document.getElementById('max_band').value;

    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'none';
    resultDiv.textContent = '';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rsi, macd_histogram, macd_line, signal_line, current_price, min_band, max_band
            })
        });
        const data = await response.json();
        if (response.ok) {
            resultDiv.innerHTML = `<b>Predicted price change:</b> ${data.predicted_price_change}%<br><b>Predicted price:</b> Rs.${data.predicted_price}`;
            resultDiv.style.display = 'block';
        } else {
            resultDiv.textContent = data.error || 'Prediction failed.';
            resultDiv.style.display = 'block';
            resultDiv.style.background = '#f8d7da';
            resultDiv.style.color = '#721c24';
        }
    } catch (err) {
        resultDiv.textContent = 'Network error. Please try again.';
        resultDiv.style.display = 'block';
        resultDiv.style.background = '#f8d7da';
        resultDiv.style.color = '#721c24';
    }
}); 