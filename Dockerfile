# Użyj oficjalnego obrazu Pythona w wersji slim
FROM python:3.10-slim

WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxinerama1 libxrandr2 libxrender1 libxtst6 libxcb-cursor0 libxcb-xinerama0 \
    libdbus-1-3 libfontconfig1 libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalacja zależności Pythona
RUN pip install --upgrade 

# Kopiowanie plików aplikacji
COPY . .

# Tworzenie i ustawienie katalogu dla konfiguracji Matplotlib
RUN mkdir -p /app/matplotlib_config
RUN chmod -R 777 /app/matplotlib_config
ENV MPLCONFIGDIR=/app/matplotlib_config


# Tworzenie katalogu konfiguracyjnego Matplotlib i ustawienie odpowiednich uprawnień
RUN mkdir -p ${MPLCONFIGDIR} && chmod -R 777 ${MPLCONFIGDIR}

CMD ["python", "main.py"]
