FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --system --deploy

COPY entrypoint.sh* src/entrypoint.sh* /app/

RUN chmod +x /app/entrypoint.sh

COPY src/ /app/

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
