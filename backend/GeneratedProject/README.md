Meteo Web App: Real-Time Weather & Clothing Advice

Overview
A full-stack web application providing real-time weather information, a 7-day forecast, air quality data, alerts, and personalized clothing recommendations. Built with React + Vite frontend and Node.js/Express backend. Uses OpenWeather APIs and Leaflet for an interactive map.

Quick start
- Prerequisites: Node 18+
- Backend
  - cd backend
  - cp .env.example .env and fill in OPENWEATHER_API_KEY
  - npm install
  - npm run dev
- Frontend
  - cd frontend
  - npm install
  - npm run dev

Tech stack
- Frontend: React, Vite, Leaflet, Tailwind (minimal), Fetch API
- Backend: Node.js, Express, node-cache

Env vars (backend)
- PORT=5050
- OPENWEATHER_API_KEY=your_key
- OPENWEATHER_BASE_URL=https://api.openweathermap.org

Monorepo scripts (optional)
- Start backend: cd backend && npm run dev
- Start frontend: cd frontend && npm run dev

Notes
- This scaffold uses a thin backend that proxies OpenWeather and adds caching and normalization. The frontend is ready to consume these endpoints and render a basic weather dashboard with clothing advice.
