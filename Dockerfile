FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "manga_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]