# 🌦️ Weather Based Clothing Recommendation System

**Weather Based Clothing Recommendation System** is an intelligent Agentic AI web application that solves the "what should I wear today?" dilemma. By analyzing real-time meteorological data, the Google Gemini AI agent suggests a curated outfit—from head to toe—tailored specifically to your local climate and current conditions.

---

## ✨ Key Features

* 🌍 **Real-Time Intelligence:** Fetches live weather data (Temperature, Humidity, Wind, Conditions) via the OpenWeather API.
* 👔 **Full Outfit Lookbook:** Generates a complete recommendation including **Top**, **Bottom**, **Footwear**, and **Accessories**.
* 🔍 **Smart City Search:** Integrated city autocomplete powered by the Open-Meteo API for a seamless user experience.
* 🧠 **Agentic Architecture:** A dedicated Python-based Flask logic layer with Google Gemini AI for intelligent decision-making.
* 📱 **Responsive Design:** A sleek, modern glassmorphism UI optimized with dynamic themes (Day, Sunset, Night) using Tailwind CSS.

---

## 🧠 System Architecture

The project utilizes a streamlined architecture to ensure a clean separation of concerns:

1. **Frontend (UI):** A responsive interface that collects user input, handles dynamic theme changes, and displays recommendations.
2. **Flask API (Backend):** Acts as the secure communication layer, routing requests and serving the application.
3. **AI Engine (Logic):** The core engine that processes weather data and executes the Gemini decision-making logic to select outfits.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| --- | --- |
| **Frontend** | HTML5, Tailwind CSS, JavaScript (ES6+) |
| **Backend** | Python 3.11, Flask, Gunicorn |
| **AI Agent** | Google Gemini API (gemini-2.0-flash / gemini-1.5-flash) |
| **APIs** | OpenWeather API & Open-Meteo Geocoding API |
| **Deployment** | Docker, Hugging Face Spaces, Render |

---

## 📁 Project Structure

```text
weather-clothing-ai/
│
├── app.py             # Flask Entry Point & AI/Weather Logic
├── requirements.txt   # Python Dependencies
├── Dockerfile         # Docker Container Configuration
├── bg.png             # UI Background Image
│
├── templates/         # User Interface
│   └── index.html     # Main Layout, Tailwind CSS & JS Logic
│
└── README.md

```

---

## ▶️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/weather-clothing-ai.git
cd weather-clothing-ai

```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Configure Environment Variables

Set your API keys in your terminal or a `.env` file:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export OPENWEATHER_API_KEY="your_openweather_api_key_here"

```

### 4. Start the Application

```bash
python app.py

```

*Runs at: `http://localhost:7860*`

---

## 🧪 Sample Output

**City:** Hyderabad

**Condition:** 25°C, Clear Sky

**Recommended Outfit:**

👕 **Top:** Lightweight Cotton T-shirt

👖 **Bottom:** Breathable Chinos

👟 **Footwear:** Canvas Sneakers

🕶️ **Accessories:** Sunglasses, Casual Watch

---

## 👤 Author
```bash
Akshay Kumar Bandla
AI & Full-Stack Development Enthusiast
```
## 📜 License

This project is intended for educational purposes only.
