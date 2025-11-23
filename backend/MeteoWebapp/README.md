Meteo Webapp — real-time weather with what-to-wear guidance

Overview
- A fast, simple weather PWA that shows real-time conditions and translates them into outfit recommendations.
- Stack: React + TypeScript + Vite (frontend), Node + Express + TypeScript (backend) proxying OpenWeather with caching.

Getting started
1) Prereqs: Node 18+
2) Setup backend
   - cd backend
   - cp ../.env.example .env
   - edit .env and paste your OpenWeather API key
   - npm install
   - npm run dev
3) Setup frontend
   - open a new terminal
   - cd frontend
   - npm install
   - npm run dev
4) Open http://localhost:5173

Scripts
- Frontend: npm run dev | build | preview | test
- Backend: npm run dev | build | start | test

Attribution
- Weather data by OpenWeather (https://openweathermap.org). Please comply with their terms.

Notes
- Caching: server-side memory cache with TTL 2–10 minutes.
- Units/language: autodetected from browser, can be changed in Settings.
- Offline: basic fallback to last known data stored locally.

