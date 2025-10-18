const $ = (id) => document.getElementById(id);

const statusEl = $('status');
const dashboard = $('dashboard');
const forecastSection = $('forecast-section');
const forecastCards = $('forecast-cards');
let forecastChart = null;

function setStatus(msg, isError=false){
  statusEl.textContent = msg;
  statusEl.className = isError ? 'status error' : 'status';
}

function showData(d){
  dashboard.classList.remove('hidden');
  $('loc-name').textContent = d.name || '';
  $('temp').textContent = d.main ? `${d.main.temp} °C` : '-';
  $('condition').textContent = d.weather && d.weather[0] ? d.weather[0].description : '-';
  $('humidity').textContent = d.main ? `${d.main.humidity}%` : '-';
  $('wind').textContent = d.wind ? `${d.wind.speed} m/s` : '-';
  $('coord').textContent = d.coord ? `${d.coord.lat}, ${d.coord.lon}` : '-';
}

function showForecast(list){
  if(!list || !list.length){
    forecastSection.classList.add('hidden');
    return;
  }
  forecastSection.classList.remove('hidden');
  // build chart data (dates and temp_avg)
  const labels = list.map(i => i.date);
  const temps = list.map(i => i.temp_avg);

  const ctx = document.getElementById('forecast-chart').getContext('2d');
  if(forecastChart) forecastChart.destroy();
  forecastChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{ label: 'Avg Temp (°C)', data: temps, borderColor: '#2b7cff', backgroundColor: 'rgba(43,124,255,0.12)', tension: 0.3 }]
    },
    options: { scales: { y: { beginAtZero: false } } }
  });

  // cards
  forecastCards.innerHTML = '';
  list.forEach(item => {
    const card = document.createElement('div');
    card.className = 'forecast-card';
    const iconUrl = item.icon ? `https://openweathermap.org/img/wn/${item.icon}@2x.png` : '';
    card.innerHTML = `
      <div class="fc-date">${item.date}</div>
      <div class="fc-icon">${iconUrl ? `<img src="${iconUrl}" alt="icon"/>` : ''}</div>
      <div class="fc-desc">${item.description || ''}</div>
      <div class="fc-temps">${item.temp_min ?? '-'}° / ${item.temp_max ?? '-'}°</div>
    `;
    forecastCards.appendChild(card);
  });
}

async function fetchWeatherByCity(city){
  setStatus('Loading...');
  try{
    const res = await fetch(`/api/weather?q=${encodeURIComponent(city)}`);
    const j = await res.json();
    if(!res.ok) throw new Error(j.error || JSON.stringify(j));
    setStatus(j.cached ? 'Loaded (cached)' : 'Loaded');
    showData(j.data);
  }catch(e){
    setStatus('Error: '+e.message, true);
    console.error(e);
  }
}

async function fetchWeatherByCoords(lat, lon){
  setStatus('Loading...');
  try{
    const res = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
    const j = await res.json();
    if(!res.ok) throw new Error(j.error || JSON.stringify(j));
    setStatus(j.cached ? 'Loaded (cached)' : 'Loaded');
    showData(j.data);
  }catch(e){
    setStatus('Error: '+e.message, true);
    console.error(e);
  }
}

document.addEventListener('DOMContentLoaded', ()=>{
  $('search-btn').addEventListener('click', ()=>{
    const city = $('city-input').value.trim();
    if(!city){ setStatus('Please enter a city', true); return; }
    fetchWeatherByCity(city);
  });

  $('geo-btn').addEventListener('click', ()=>{
    if(!navigator.geolocation){ setStatus('Geolocation not supported', true); return; }
    setStatus('Getting location...');
    navigator.geolocation.getCurrentPosition((pos)=>{
      fetchWeatherByCoords(pos.coords.latitude, pos.coords.longitude);
      fetchForecastByCoords(pos.coords.latitude, pos.coords.longitude);
    }, (err)=>{
      setStatus('Geolocation error: '+err.message, true);
    });
  });
});

async function fetchForecastByCoords(lat, lon){
  setStatus('Loading forecast...');
  try{
    const res = await fetch(`/api/forecast?lat=${lat}&lon=${lon}`);
    const j = await res.json();
    if(!res.ok) throw new Error(j.error || JSON.stringify(j));
    setStatus('Forecast loaded');
    showForecast(j.data);
  }catch(e){
    setStatus('Forecast error: '+e.message, true);
    console.error(e);
  }
}

async function fetchForecastByCity(city){
  setStatus('Loading forecast...');
  try{
    const res = await fetch(`/api/forecast?q=${encodeURIComponent(city)}`);
    const j = await res.json();
    if(!res.ok) throw new Error(j.error || JSON.stringify(j));
    setStatus('Forecast loaded');
    showForecast(j.data);
  }catch(e){
    setStatus('Forecast error: '+e.message, true);
    console.error(e);
  }
}

// call forecast on search
document.addEventListener('DOMContentLoaded', ()=>{
  $('search-btn').addEventListener('click', ()=>{
    const city = $('city-input').value.trim();
    if(!city){ setStatus('Please enter a city', true); return; }
    fetchWeatherByCity(city);
    fetchForecastByCity(city);
  });
});
