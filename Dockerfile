# Basis-Image
FROM python:3.11-slim

# Umgebungsvariablen für Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Arbeitsverzeichnis (Root)
WORKDIR /app

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den gesamten Code kopieren
COPY . .

# WICHTIG: Wir wechseln in das Unterverzeichnis "backend"
WORKDIR /app/backend

# User erstellen (Sicherheit)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Port freigeben
EXPOSE 8000

# Startbefehl
# Da wir durch WORKDIR bereits in /app/backend sind, rufen wir direkt "main:app" auf.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
