# Brand Mention Tracker - Full Project

This repository is a full Django application for the Brand Mention Tracker demo.

## Features

- **Django backend** with ASGI + Channels + Celery
- **Transformer-based NLP** for sentiment analysis in `tracker/nlp.py`
- **Django templates** with Tailwind CSS for the frontend (no React required!)
- **Real-time updates** via WebSocket (Django Channels)
- **RSS feed monitoring** with automatic sentiment analysis
- **Dashboard** with statistics and charts (Chart.js)
- **Docker support** with docker-compose files

## Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Redis (optional, for Celery and WebSocket support)
- pip

### Setup Steps

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start Redis (optional but recommended):**
   ```bash
   # On Windows, download Redis from: https://github.com/microsoftarchive/redis/releases
   # On macOS: brew install redis && redis-server
   # On Linux: sudo apt-get install redis-server && redis-server
   ```

5. **Start Celery worker (optional, for background tasks):**
   ```bash
   celery -A brandtracker worker -l info
   ```

6. **Start Django development server:**
   ```bash
   python manage.py runserver
   ```

7. **Open your browser:**
   Navigate to `http://localhost:8000`

## Usage

- **Dashboard** (`/dashboard/`): View statistics, sentiment breakdown, and charts
- **Mentions** (`/mentions/`): Browse all brand mentions with filtering
- **Alerts** (`/alerts/`): Real-time alerts for negative sentiment spikes
- **RSS Feeds** (`/feeds/`): Add and manage RSS feed sources

## Notes

- The app works without Redis/Celery, but background processing will run synchronously
- WebSocket support requires Redis for production (uses in-memory fallback in development)
- The frontend is built entirely with Django templates - no separate frontend build step needed!

## Docker

To run with Docker:
```bash
docker-compose up
```

## API Endpoints

The REST API endpoints are still available at `/api/` for programmatic access:
- `/api/mentions/` - List mentions
- `/api/alerts/` - List alerts
- `/api/dashboard-stats/` - Dashboard statistics
- `/api/start-fetch/` - Start RSS feed fetch (POST)
