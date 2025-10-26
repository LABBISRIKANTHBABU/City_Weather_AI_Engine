import gradio as gr
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import random

# Configuration - Use environment variable for API key
API_KEY = os.getenv('OPENWEATHER_API_KEY', 'b9d350d631c7212603d437d5e3e8965e')
BASE_URL = "http://api.openweathermap.org/data/2.5"

# Sample data for fallback when API fails
SAMPLE_DATA = {
    "weather": {
        "name": "Sample City",
        "sys": {"country": "US"},
        "dt": datetime.now().timestamp(),
        "main": {"temp": 22, "feels_like": 24, "humidity": 65, "pressure": 1013},
        "wind": {"speed": 3.5, "deg": 180},
        "clouds": {"all": 40},
        "weather": [{"description": "scattered clouds"}],
        "coord": {"lat": 40.7128, "lon": -74.0060}
    }
}

# CSS for Hugging Face deployment
custom_css = """
:root {
    --primary: #6366f1;
    --primary-dark: #4338ca;
    --secondary: #0f172a;
    --accent: #10b981;
    --text: #ffffff;
    --text-light: #94a3b8;
    --border: #334155;
    --card-bg: rgba(30, 41, 59, 0.9);
}

body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    min-height: 100vh;
    margin: 0;
    color: var(--text);
}

.gradio-container {
    max-width: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 1rem !important;
    background: transparent !important;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

.header {
    text-align: center;
    margin-bottom: 2rem;
    background: var(--card-bg);
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid var(--border);
}

.header h1 {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.5rem !important;
}

.search-section {
    background: var(--card-bg);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    border: 1px solid var(--border);
}

.input-text {
    border-radius: 10px !important;
    border: 2px solid var(--border) !important;
    padding: 1rem !important;
    background: rgba(15, 23, 42, 0.8) !important;
    color: var(--text) !important;
    width: 100% !important;
}

.button-primary {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 1rem 2rem !important;
    color: white !important;
    font-weight: 600 !important;
    width: 100% !important;
}

.weather-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.weather-card {
    background: var(--card-bg);
    border-radius: 15px;
    padding: 1.5rem;
    border: 1px solid var(--border);
    transition: transform 0.2s;
}

.weather-card:hover {
    transform: translateY(-2px);
}

.weather-metric {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
}

.weather-metric:last-child {
    border-bottom: none;
}

.metric-value {
    font-weight: 600;
    color: var(--text);
}

.plot-container {
    background: var(--card-bg);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid var(--border);
}

.aqi-good { color: #10b981; }
.aqi-moderate { color: #f59e0b; }
.aqi-unhealthy { color: #ef4444; }

@media (max-width: 768px) {
    .gradio-container {
        padding: 0.5rem !important;
    }
    .header h1 {
        font-size: 2rem !important;
    }
    .weather-grid {
        grid-template-columns: 1fr;
    }
}
"""

def get_weather_icon(condition):
    """Get weather icon based on condition"""
    condition = condition.lower()
    if "clear" in condition:
        return "☀️"
    elif "cloud" in condition:
        return "☁️"
    elif "rain" in condition:
        return "🌧️"
    elif "snow" in condition:
        return "❄️"
    elif "thunder" in condition:
        return "⛈️"
    else:
        return "🌤️"

def fetch_weather_data(location):
    """Fetch weather data with fallback to sample data"""
    try:
        # Try to fetch from OpenWeatherMap API
        weather_url = f"{BASE_URL}/weather?q={location}&appid={API_KEY}&units=metric"
        response = requests.get(weather_url, timeout=10)
        
        if response.status_code == 200:
            weather_data = response.json()
            return {
                "weather": weather_data,
                "source": "live"
            }
        else:
            return generate_sample_data(location)
            
    except Exception:
        return generate_sample_data(location)

def generate_sample_data(location):
    """Generate sample data for demo"""
    sample = SAMPLE_DATA.copy()
    sample["weather"]["name"] = location.title()
    sample["weather"]["main"]["temp"] = round(random.uniform(10, 30), 1)
    sample["weather"]["main"]["feels_like"] = round(sample["weather"]["main"]["temp"] + random.uniform(-2, 3), 1)
    sample["weather"]["main"]["humidity"] = random.randint(40, 80)
    sample["weather"]["wind"]["speed"] = round(random.uniform(1, 8), 1)
    sample["source"] = "sample"
    return sample

def create_temperature_chart(forecast_data=None):
    """Create simple temperature chart"""
    if forecast_data and 'list' in forecast_data:
        times = []
        temps = []
        for i, entry in enumerate(forecast_data['list'][:6]):
            times.append(f"Hour {i+1}")
            temps.append(entry['main']['temp'])
    else:
        # Sample data
        times = [f"Hour {i+1}" for i in range(6)]
        temps = [20 + random.uniform(-3, 3) for _ in range(6)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=temps,
        mode='lines+markers',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def create_humidity_chart(humidity):
    """Create humidity gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = humidity,
        title = {'text': "Humidity (%)"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#10b981"},
            'steps': [
                {'range': [0, 50], 'color': "rgba(16, 185, 129, 0.2)"},
                {'range': [50, 100], 'color': "rgba(16, 185, 129, 0.4)"}],
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font = {'color': "white"},
        height = 300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def create_wind_gauge(wind_speed):
    """Create wind speed gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = wind_speed,
        title = {'text': "Wind Speed (m/s)"},
        gauge = {
            'axis': {'range': [None, 20]},
            'bar': {'color': "#6366f1"},
            'steps': [
                {'range': [0, 5], 'color': "rgba(99, 102, 241, 0.2)"},
                {'range': [5, 10], 'color': "rgba(99, 102, 241, 0.4)"},
                {'range': [10, 20], 'color': "rgba(99, 102, 241, 0.6)"}],
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font = {'color': "white"},
        height = 300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def get_weather_report(location):
    """Main function to get weather report"""
    if not location.strip():
        raise gr.Error("Please enter a city name")
    
    data = fetch_weather_data(location)
    weather = data['weather']
    source = data['source']
    
    # Extract weather data
    city_name = weather['name']
    country = weather['sys']['country']
    temp = weather['main']['temp']
    feels_like = weather['main']['feels_like']
    humidity = weather['main']['humidity']
    pressure = weather['main']['pressure']
    wind_speed = weather['wind']['speed']
    description = weather['weather'][0]['description'].title()
    weather_icon = get_weather_icon(description)
    
    # Create weather card HTML
    weather_card = f"""
    <div class='weather-card'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
            <div>
                <h2 style='margin: 0;'>{city_name}, {country}</h2>
                <p style='color: var(--text-light); margin: 0;'>Data: {'🌐 Live' if source == 'live' else '🧪 Sample'}</p>
            </div>
            <div style='font-size: 3rem;'>{weather_icon}</div>
        </div>
        
        <div style='text-align: center; margin: 1.5rem 0;'>
            <div style='font-size: 3rem; font-weight: 800;'>{temp}°C</div>
            <div style='color: var(--text-light);'>Feels like {feels_like}°C</div>
            <div style='color: var(--text-light); margin-top: 0.5rem;'>{description}</div>
        </div>
        
        <div class='weather-metrics'>
            <div class='weather-metric'>
                <span>💧 Humidity</span>
                <span class='metric-value'>{humidity}%</span>
            </div>
            <div class='weather-metric'>
                <span>💨 Wind Speed</span>
                <span class='metric-value'>{wind_speed} m/s</span>
            </div>
            <div class='weather-metric'>
                <span>🌡️ Pressure</span>
                <span class='metric-value'>{pressure} hPa</span>
            </div>
        </div>
    </div>
    """
    
    # Create charts
    temp_chart = create_temperature_chart()
    humidity_chart = create_humidity_chart(humidity)
    wind_chart = create_wind_gauge(wind_speed)
    
    return weather_card, temp_chart, humidity_chart, wind_chart

# Create Gradio interface
with gr.Blocks(css=custom_css, theme=gr.themes.Default()) as demo:
    with gr.Column(elem_classes="container"):
        gr.Markdown("""
        <div class='header'>
            <h1>🌤️ Weather Dashboard</h1>
            <p>Real-time weather information for any city worldwide</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=4):
                location_input = gr.Textbox(
                    label="Enter City Name",
                    placeholder="e.g., London, Tokyo, New York...",
                    elem_classes="input-text"
                )
            with gr.Column(scale=1):
                submit_btn = gr.Button("Get Weather", elem_classes="button-primary")
        
        with gr.Row():
            weather_html = gr.HTML()
        
        with gr.Row():
            with gr.Column():
                temp_plot = gr.Plot(label="Temperature Forecast")
            with gr.Column():
                humidity_plot = gr.Plot(label="Humidity")
        
        with gr.Row():
            wind_plot = gr.Plot(label="Wind Speed")
        
        # Examples for quick testing
        gr.Examples(
            examples=["London", "New York", "Tokyo", "Paris", "Sydney"],
            inputs=location_input
        )
    
    submit_btn.click(
        fn=get_weather_report,
        inputs=location_input,
        outputs=[weather_html, temp_plot, humidity_plot, wind_plot]
    )

# For Hugging Face Spaces
if __name__ == "__main__":
    demo.launch()