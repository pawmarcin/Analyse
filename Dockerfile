FROM python:3.10-slim

WORKDIR /app

# Instalacja zależności systemowych dla Matplotlib i Qt
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-randr0 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-xinerama0 \
    libxcb-shm0 \
    libxcb-icccm4 \
    libxcb-sync1 \
    libxcb-xkb1 \
    libxcb-glx0 \
    libx11-xcb1 \
    libgl1-mesa-glx \
    libxi6 \
    libxrender1 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libfreetype6 \
    libdbus-1-3 \
    libxext6 \
    qt5-qmake \
    qtbase5-dev-tools \
    qtchooser \
    qtmultimedia5-dev \
    && rm -rf /var/lib/apt/lists/*
    
# Tworzenie i ustawienie katalogu dla konfiguracji Matplotlib
RUN mkdir -p /app/matplotlib_config
RUN chmod -R 777 /app/matplotlib_config
ENV MPLCONFIGDIR=/app/matplotlib_config

# Aktualizacja pip i instalacja zależności Pythona
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
