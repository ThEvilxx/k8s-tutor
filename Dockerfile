FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_DEBUG=False
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY manage.py .
COPY config/ config/
COPY practice/ practice/
COPY templates/ templates/
COPY static/ static/
RUN DJANGO_SECRET_KEY=build-only-placeholder python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","1","--timeout","45","--access-logfile","-","--error-logfile","-"]
