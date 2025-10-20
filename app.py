import os
import time
# from datetime import timedelta  (unused)

from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# Simple in-memory cache: {cache_key: (timestamp, data)}
CACHE = {}
CACHE_TTL = 300  # seconds


def cache_get(key):
    entry = CACHE.get(key)
    if not entry:
        return None
    ts, data = entry
    if time.time() - ts > CACHE_TTL:
        del CACHE[key]
        return None
    return data


def cache_set(key, data):
    CACHE[key] = (time.time(), data)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/weather')
def weather_api():
    """Proxy to OpenWeatherMap Current Weather API.

    Query params:
      q: city name (e.g., London) OR
      lat & lon: coordinates
    """
    # Read API key at request time so tests can monkeypatch the environment.
    api_key = os.getenv("OPENWEATHER_API_KEY") or ""
    if not api_key.strip():
        return jsonify({'error': 'Server misconfigured: OPENWEATHER_API_KEY not set'}), 500
    
    q = request.args.get('q')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not q and not (lat and lon):
        return jsonify({'error': 'Provide q=city or lat & lon'}), 400

    params = {'appid': api_key, 'units': 'metric'}
    cache_key = None
    if q:
        params['q'] = q
        cache_key = f'q:{q}'
    else:
        params['lat'] = lat
        params['lon'] = lon
        cache_key = f'lat:{lat}|lon:{lon}'

    cached = cache_get(cache_key)
    if cached:
        return jsonify({'cached': True, 'data': cached})

    url = 'https://api.openweathermap.org/data/2.5/weather'
    try:
        resp = requests.get(url, params=params, timeout=5)
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to reach weather service', 'detail': str(e)}), 502

    if resp.status_code != 200:
        return jsonify({'error': 'Weather API error', 'detail': resp.text}), resp.status_code

    data = resp.json()
    # Minimal transformation: pick what frontend needs
    out = {
        'name': data.get('name'),
        'coord': data.get('coord'),
        'weather': data.get('weather'),
        'main': data.get('main'),
        'wind': data.get('wind'),
        'sys': data.get('sys'),
    }
    cache_set(cache_key, out)
    return jsonify({'cached': False, 'data': out})


@app.route('/api/forecast')
def forecast_api():
    """Proxy to OpenWeatherMap 5 day / 3 hour forecast API.

    Query params:
      q: city name OR lat & lon
    Returns daily summaries (date, min/max temp, condition, icon)
    """
    api_key = os.getenv("OPENWEATHER_API_KEY") or ""
    if not api_key.strip():
        return jsonify({'error': 'Server misconfigured: OPENWEATHER_API_KEY not set'}), 500

    q = request.args.get('q')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not q and not (lat and lon):
        return jsonify({'error': 'Provide q=city or lat & lon'}), 400

    params = {'appid': api_key, 'units': 'metric'}
    cache_key = None
    if q:
        params['q'] = q
        cache_key = f'forecast:q:{q}'
    else:
        params['lat'] = lat
        params['lon'] = lon
        cache_key = f'forecast:lat:{lat}|lon:{lon}'

    cached = cache_get(cache_key)
    if cached:
        return jsonify({'cached': True, 'data': cached})

    url = 'https://api.openweathermap.org/data/2.5/forecast'
    try:
        resp = requests.get(url, params=params, timeout=6)
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to reach forecast service', 'detail': str(e)}), 502

    payload = resp.json()
    # Summarize 3-hour slots into daily summaries
    from collections import defaultdict
    days = defaultdict(list)
    for item in payload.get('list', []):
        # item['dt_txt'] like '2025-10-18 12:00:00'
        day = item['dt_txt'].split(' ')[0]
        days[day].append(item)

    daily = []
    for day, items in sorted(days.items()):
        temps = [it['main']['temp'] for it in items if 'main' in it]
        mins = [it['main']['temp_min'] for it in items if 'main' in it]
        maxs = [it['main']['temp_max'] for it in items if 'main' in it]
        # pick the most frequent weather icon/description
        from collections import Counter
        conds = [it['weather'][0] for it in items if it.get('weather')]
        most = Counter([c['icon'] + '|' + c.get('description','') for c in conds]).most_common(1)
        icon, desc = (most[0][0].split('|')[0], most[0][0].split('|')[1]) if most else (None, None)
        daily.append({
            'date': day,
            'temp_avg': round(sum(temps) / len(temps), 1) if temps else None,
            'temp_min': round(min(mins), 1) if mins else None,
            'temp_max': round(max(maxs), 1) if maxs else None,
            'icon': icon,
            'description': desc,
        })

    cache_set(cache_key, daily)
    return jsonify({'cached': False, 'data': daily})


if __name__ == '__main__':
    # For local dev only. Use env FLASK_ENV=development for debug.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
