# Użyj oficjalnego obrazu Pythona w wersji slim
FROM python:3.10-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxinerama1 libxrandr2 libxrender1 libxtst6 libxcb-cursor0 libxcb-xinerama0 \
    && rm -rf /var/lib/apt/lists/*

# Aktualizacja pip
RUN pip install --upgrade pip

# Kopiowanie tylko pliku requirements.txt najpierw, aby skorzystać z cache Docker
COPY requirements.txt .
# Instalacja zależności Pythona z pliku requirements.txt
RUN pip install -r requirements.txt

# Kopiowanie reszty plików projektu
COPY . .

# Utworzenie zapisywalnego katalogu dla Matplotlib
RUN mkdir -p /app/matplotlib_config && chmod u+w /app/matplotlib_config
# Ustawienie zmiennej środowiskowej dla Matplotlib
ENV MPLCONFIGDIR=/app/matplotlib_config

# Uruchomienie aplikacji
CMD ["python", "main.py"]
