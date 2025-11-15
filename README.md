# Brand Mention Tracker - Full Project (scaffold)

This repository is a full Django scaffold for the Brand Mention Tracker demo.

Files include:
- Django backend (ASGI + Channels + Celery)
- Transformer-based NLP in tracker/nlp.py
- Basic frontend (Django templates) and a separate React+Tailwind frontend in /frontend
- Docker and docker-compose files

See the in-chat canvas 'Brand Mention Tracker - Complete Code' for the original full content and explanations.

Run instructions (local):
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python manage.py migrate
5. redis-server
6. celery -A brandtracker worker -l info
7. python manage.py runserver

For frontend:
cd frontend
npm install
npm run start
