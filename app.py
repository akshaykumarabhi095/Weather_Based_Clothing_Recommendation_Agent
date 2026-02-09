import os
import json
import requests
import urllib3
import time
from flask import Flask, render_template, request, jsonify
from flask_caching import Cache  # <--- NEW: Import Cache

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ==========================================
# ⚡ CONFIGURATION & CACHE SETUP
# ==========================================
# Cache config: Stores data in memory (RAM) for speed
app.config['CACHE_TYPE'] = 'SimpleCache' 
app.config['CACHE_DEFAULT_TIMEOUT'] = 600 # 10 Minutes
cache = Cache(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

# Create a session to reuse connections (Faster than opening new ones)
http = requests.Session()

def get_mock_clothing():
    return json.dumps({
        "headline": "Classic Style",
        "reasoning": "Offline Mode: AI connection unavailable.",
        "outfit_top": "Cotton T-Shirt",
        "outfit_bottom": "Comfortable Jeans",
        "shoes": "Sneakers",
        "accessories": ["Watch", "Sunglasses"]
    })

def call_gemini_with_retry(prompt):
    """
    Optimized Retry Logic:
    - Reduced wait time from 2s -> 1.5s
    - Toggles models to find a free lane faster
    """
    cycle_models = ["gemini-2.5-flash", "gemini-2.0-flash"]
    max_total_attempts = 6  # Reduced from 10 to prevent 20s waits
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for i in range(max_total_attempts):
        current_model = cycle_models[i % len(cycle_models)]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={GEMINI_API_KEY}"
        
        try:
            print(f"🤖 {current_model} (Attempt {i+1})...")
            # Use session 'http' for speed
            response = http.post(url, headers=headers, json=payload, verify=False, timeout=8)
            
            if response.status_code == 200:
                print(f"✅ Success with {current_model}!")
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            
            elif response.status_code == 429:
                print(f"⚠️ {current_model} is busy. Sleeping 1s...")
                time.sleep(1.5) # Reduced sleep time
                continue 
            
            else:
                time.sleep(1)
                continue

        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            time.sleep(1)

    print("❌ All AI attempts failed.")
    return None

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/autocomplete', methods=['GET'])
@cache.cached(timeout=300, query_string=True) # <--- CACHE THIS: Saves city searches for 5 mins
def autocomplete():
    query = request.args.get('q', '')
    if len(query) < 2: return jsonify([])
    
    # Open-Meteo is fast, but caching makes it instant for repeated searches
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
    try:
        response = http.get(url, verify=False, timeout=3)
        data = response.json()
        suggestions = []
        if 'results' in data:
            for city in data['results']:
                suggestions.append({
                    "label": f"{city['name']}, {city.get('country', '')} ({city.get('admin1', '')})",
                    "lat": city['latitude'],
                    "lon": city['longitude']
                })
        return jsonify(suggestions)
    except:
        return jsonify([])

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    try:
        data = request.json
        city_label = data.get('city', 'unknown')
        
        # ⚡ CHECK CACHE FIRST ⚡
        # If we already generated an outfit for this city today, return it instantly!
        cache_key = f"rec_{city_label}_{data['lat']}"
        cached_response = cache.get(cache_key)
        if cached_response:
            print(f"⚡ Serving from Cache: {city_label}")
            return jsonify(cached_response)

        print(f"\n👕 New Request: {city_label}")

        # 1. FETCH WEATHER
        weather_ctx = {"temp": 25, "condition": "Unknown", "wind": 5, "humidity": 50}
        try:
            w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={data['lat']}&lon={data['lon']}&appid={OPENWEATHER_API_KEY}&units=metric"
            w_res = http.get(w_url, verify=False, timeout=5).json()
            
            if w_res.get('cod') == 200:
                weather_ctx = {
                    "temp": round(w_res['main']['temp']),
                    "feels_like": round(w_res['main']['feels_like']),
                    "humidity": w_res['main']['humidity'],
                    "wind": round(w_res['wind']['speed'] * 3.6),
                    "condition": w_res['weather'][0]['description'].title()
                }
        except Exception as e:
            print(f"⚠️ Weather Error: {e}")

        # 2. CALL AI
        prompt = f"""
        Act as a Style Agent. 
        Weather: {weather_ctx['temp']}C, {weather_ctx['condition']}.
        
        Return STRICT JSON: {{
            "headline": "Short Headline", "outfit_top": "Top", "outfit_bottom": "Bottom", 
            "shoes": "Shoes", "accessories": ["Item1"], "reasoning": "Why"
        }}
        """
        
        ai_text = call_gemini_with_retry(prompt)
        
        result_data = {"weather": weather_ctx, "agent_response": get_mock_clothing()}
        
        if ai_text:
            clean_text = ai_text.replace("```json", "").replace("```", "").strip()
            result_data["agent_response"] = clean_text
            
            # SAVE TO CACHE for 10 minutes (600s)
            cache.set(cache_key, result_data, timeout=600)

        return jsonify(result_data)

    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)