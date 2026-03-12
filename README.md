# FloodSense AI | Urban Flood Intelligence System 🌊🤖

FloodSense AI is a next-generation urban resilience monitoring system designed to predict flood risks, detect micro-hotspots, and provide real-time recommendations for city wards. Built for modern urban management and emergency response.

## ✨ Key Features
- **Predictive AI Modeling**: Dynamic risk assessment based on rainfall, drainage capacity, and elevation data.
- **Cyber-Monitoring Dashboard**: A high-end dark-themed UI with real-time analytics and glassmorphism.
- **Interactive Geospatial Mapping**: Professional Leaflet-based map with color-coded risk zones and ward boundaries.
- **Real-time Simulation Engine**: Instantly visualize how rainfall increases impact city-wide safety.
- **Actionable AI Insights**: Detailed per-ward reports with prioritized emergency response actions.

## 🚀 Quick Start

### 1. Backend API (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt
python serve.py
```
- **API Base**: `http://127.0.0.1:8000`

### 2. Frontend Dashboard (React + Tailwind)
```bash
cd frontend
python -m http.server 5173
```
- **Dashboard**: `http://localhost:5173`

## 📂 Project Structure
- `backend/`: FastAPI application, risk services, and geospatial data.
- `frontend/`: Modern React dashboard (Self-contained & Vite versions).
- `data/`: CSV datasets for rainfall, elevation, and urban drainage.

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI, Pandas, Scikit-learn
- **Frontend**: React, Tailwind CSS, Leaflet.js, Recharts, Lucide Icons
- **Deployment**: Local HTTP Server / Uvicorn

---
*Developed for Urban Flood Intelligence Hackathon 2026*
