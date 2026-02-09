import os
import json
import requests
import urllib3
import time  # <--- Added for waiting
from flask import Flask, render_template, request, jsonify

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ==========================================
# 👇 YOUR KEYS ARE HERE 👇
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
# ==========================================

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
    1. Tries the NEWEST models first (2.5 Flash).
    2. If busy (429), WAITS 3 seconds and Retries.
    """
    # Optimized list based on your account permissions
    models = [
        "gemini-2.5-flash",       # ✅ Try the newest one first (Less busy)
        "gemini-2.0-flash",       # Standard 2.0
        "gemini-2.0-flash-lite",  # Backup
        "gemini-2.0-flash-001"    # Specific version fallback
    ]
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        
        # Try each model up to 2 times
        for attempt in range(2):
            try:
                print(f"🤖 {model} (Attempt {attempt+1})...")
                response = requests.post(url, headers=headers, json=payload, verify=False, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Success with {model}!")
                    return response.json()['candidates'][0]['content']['parts'][0]['text']
                
                elif response.status_code == 429:
                    print(f"⚠️ {model} is busy. Waiting 3s...")
                    time.sleep(3) # WAIT before retrying
                    continue 
                
                elif response.status_code == 404:
                    print(f"❌ {model} not found. Skipping.")
                    break # Don't retry a 404, move to next model
                
                else:
                    print(f"❌ Error {response.status_code}. Skipping.")
                    break

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
def autocomplete():
    query = request.args.get('q', '')
    if len(query) < 2: return jsonify([])
    
    # Use Open-Meteo for searching (Better for Indian cities)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
    try:
        response = requests.get(url, verify=False, timeout=5)
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
        print(f"\n👕 Request: {data.get('city')}")

        # 1. FETCH WEATHER (OpenWeatherMap)
        weather_ctx = {"temp": 25, "condition": "Unknown", "wind": 5, "humidity": 50}
        try:
            w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={data['lat']}&lon={data['lon']}&appid={OPENWEATHER_API_KEY}&units=metric"
            w_res = requests.get(w_url, verify=False, timeout=5).json()
            
            if w_res.get('cod') == 200:
                weather_ctx = {
                    "temp": round(w_res['main']['temp']),
                    "feels_like": round(w_res['main']['feels_like']),
                    "humidity": w_res['main']['humidity'],
                    "wind": round(w_res['wind']['speed'] * 3.6),
                    "condition": w_res['weather'][0]['description'].title()
                }
                print(f"🌤️ Weather: {weather_ctx['temp']}°C, {weather_ctx['condition']}")
        except Exception as e:
            print(f"⚠️ Weather Error: {e}")

        # 2. CALL AI
        prompt = f"""
        Act as a Style Agent. 
        Weather: {weather_ctx['temp']}C (Feels like {weather_ctx.get('feels_like')}C), {weather_ctx['condition']}.
        Humidity: {weather_ctx['humidity']}%, Wind: {weather_ctx['wind']} km/h.
        
        Return STRICT JSON (no markdown): {{
            "headline": "Short Headline", "outfit_top": "Top", "outfit_bottom": "Bottom", 
            "shoes": "Shoes", "accessories": ["Item1"], "reasoning": "Why"
        }}
        """
        
        ai_text = call_gemini_with_retry(prompt)
        
        if ai_text:
            clean_text = ai_text.replace("```json", "").replace("```", "").strip()
            return jsonify({"weather": weather_ctx, "agent_response": clean_text})
        else:
            return jsonify({"weather": weather_ctx, "agent_response": get_mock_clothing()})

    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)