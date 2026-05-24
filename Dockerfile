# Używamy lekkiego, oficjalnego obrazu Pythona
FROM python:3.9-slim

# Ustawiamy katalog roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy plik z listą bibliotek i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu aplikacji do kontenera
COPY . .

# Wystawiamy port 5000 na zewnątrz kontenera
EXPOSE 5000

# Komenda uruchamiająca serwer
CMD ["python", "run.py"]