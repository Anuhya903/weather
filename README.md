# Weather Dashboard (Flask)

A small full-stack Python project: Flask backend that proxies OpenWeatherMap and a simple JavaScript frontend dashboard.

Quick start (Windows PowerShell):

1. Create a virtual environment and install deps

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Create a `.env` file with your OpenWeatherMap API key (or set env variable directly)

```text
OPENWEATHER_API_KEY=your_api_key_here
```

3. Run the app

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

Notes:
- This uses the OpenWeatherMap Current Weather API. Get a free API key at https://openweathermap.org.
- The server includes a tiny in-memory cache (300s) to avoid repeated API calls during testing.
