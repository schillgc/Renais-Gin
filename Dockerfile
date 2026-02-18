FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client gcc python3-dev libpq-dev libjpeg-dev zlib1g-dev curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn psycopg2-binary
COPY renais_gin /app/
RUN mkdir -p /app/media/qr_codes /app/media/pdfs/user_uploads /app/media/pdfs/generated_reports /app/staticfiles /app/logs
RUN useradd -m -u 1000 renais && chown -R renais:renais /app
USER renais
EXPOSE 8000
CMD ["gunicorn", "renais_gin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]