web: gunicorn legalai.wsgi:application --chdir backend --bind 0.0.0.0:$PORT --workers 4 --timeout 300
worker: celery -A legalai worker --loglevel=info --chdir backend
