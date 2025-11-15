FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run migrations and start the server
CMD sh -c "python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT} brandtracker.asgi:application"
