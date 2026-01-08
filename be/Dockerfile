# Dockerfile

# Verwende ein stabiles, voll ausgestattetes Python-Image
FROM python:3.12

# FÜR PSYCOPG2: Installiere notwendige System-Header
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Kopiere requirements.txt
COPY requirements.txt /app/

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den gesamten Projektcode in den Container
COPY . /app/

# --- ENTRYPOINT LOGIK ---
# Kopiere das Entrypoint-Skript und mache es ausführbar
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Der Einstiegspunkt des Containers ist das Shell-Skript
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Das Kommando (runserver) wird an das Skript übergeben
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]