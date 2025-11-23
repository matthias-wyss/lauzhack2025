import React, { useEffect, useState } from 'react';
import MapView from './components/MapView.jsx';
import SearchBar from './components/SearchBar.jsx';
import WeatherPanel from './components/WeatherPanel.jsx';
import AdvicePanel from './components/AdvicePanel.jsx';
import Forecast from './components/Forecast.jsx';
import AlertsBar from './components/AlertsBar.jsx';
import AQI from './components/AQI.jsx';
import LanguageSwitcher from './components/LanguageSwitcher.jsx';
import FavoritesList from './components/FavoritesList.jsx';
import RecentSearches from './components/RecentSearches.jsx';
import useWeather from './hooks/useWeather.js';
import useGeolocation from './hooks/useGeolocation.js';

export default function App() {
  const [query, setQuery] = useState('');
  const [coords, setCoords] = useState(null);
  const { position, error: geoError } = useGeolocation();
  const weather = useWeather(coords);

  useEffect(() => {
    if (position && !coords) {
      setCoords({ lat: position.coords.latitude, lon: position.coords.longitude });
    }
  }, [position]);

  function handleSelectPlace(place) {
    if (place && place.lat && place.lon) {
      setCoords({ lat: place.lat, lon: place.lon });
      setQuery(place.label || '');
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Meteo</h1>
        <LanguageSwitcher />
      </header>
      <main className="layout">
        <section className="left">
          <SearchBar query={query} onChange={setQuery} onSelect={handleSelectPlace} />
          <MapView coords={coords} onSelect={handleSelectPlace} weather={weather.data} />
          <div className="lists">
            <FavoritesList onSelect={handleSelectPlace} />
            <RecentSearches onSelect={handleSelectPlace} />
          </div>
        </section>
        <section className="right">
          <AlertsBar alerts={weather.data?.alerts} loading={weather.loading} />
          <WeatherPanel weather={weather.data} loading={weather.loading} />
          <AdvicePanel weather={weather.data} loading={weather.loading} />
          <Forecast forecast={weather.data?.daily} loading={weather.loading} />
          <AQI aqi={weather.data?.aqi} loading={weather.loading} />
        </section>
      </main>
      <footer className="app-footer">Data by OpenWeather • Map by OpenStreetMap/Leaflet</footer>
      {geoError && <div className="toast">Geolocation error: {geoError.message}</div>}
    </div>
  );
}
