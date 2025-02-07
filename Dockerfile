# Użyj oficjalnego obrazu Pythona w wersji slim
FROM python:3.10-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxinerama1 libxrandr2 libxrender1 libxtst6 libxcb-cursor0 libxcb-xinerama0 \
    libxcb-1-0 libdbus-1-3 libfontconfig1 libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Aktualizacja pip
RUN pip install --upgrade pip

# Kopiowanie tylko pliku requirements.txt najpierw, aby skorzystać z cache Docker
COPY requirements.txt .
# Instalacja zależności Pythona z pliku requirements.txt
RUN pip install -r requirements.txt

# Kopiowanie reszty plików projektu
COPY . .

RUN mkdir -p /app/matplotlib_config
RUN chmod -R 777 /app/matplotlib_config
ENV MPLCONFIGDIR=/app/matplotlib_config

# Uruchomienie aplikacji
CMD ["python", "main.py"]
