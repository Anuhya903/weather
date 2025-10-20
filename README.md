# Weather Dashboard (Flask)

A small full-stack Python project: Flask backend that proxies OpenWeatherMap and a simple JavaScript frontend dashboard.

## 🌐 Live Demo
**Live Application:** [https://weather-dashboard-dv.onrender.com](https://weather-dashboard-dv.onrender.com)

## 🚀 Quick Start (Local Development)

### 1. Create a virtual environment and install dependencies
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Create a .env file with your OpenWeatherMap API key
```env
OPENWEATHER_API_KEY=your_api_key_here
```

### 3. Run the app
```bash
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## 🛠️ Features
- **Current Weather** - Real-time weather data for any city
- **5-Day Forecast** - Extended weather predictions
- **Responsive Design** - Works on desktop and mobile devices
- **Caching System** - Reduces API calls with in-memory cache

## 📁 Project Structure
```
weather/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (not in git)
├── static/
│   ├── styles.css        # Frontend styles
│   └── main.js           # Frontend JavaScript
└── templates/
    └── index.html        # Main dashboard page
```

## 🔧 Technologies Used
- **Backend:** Python, Flask
- **Frontend:** JavaScript, HTML, CSS
- **API:** OpenWeatherMap
- **Deployment:** Render
- **Security:** Environment variables, Secure configuration

## 📝 Notes
- This uses the OpenWeatherMap Current Weather API. Get a free API key at [https://openweathermap.org](https://openweathermap.org)
- The server includes a tiny in-memory cache (300s) to avoid repeated API calls during testing
- **Production version** deployed on Render with secure environment variables

## 🔒 Security
- API keys are stored securely in environment variables
- Never committed to version control
- Production secrets managed through Render environment variables

---

*Live demo deployed on Render - may take 30-50 seconds to wake up after inactivity*
