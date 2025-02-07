FROM python:3.10-slim

WORKDIR /app

# Instalacja zależności systemowych dla Matplotlib i Qt
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxinerama1 libxrandr2 libxrender1 libxtst6 libxcb-cursor0 libxcb-xinerama0 \
    libdbus-1-3 libfontconfig1 libxkbcommon-x11-0 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xfixes0 libegl1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Tworzenie i ustawienie katalogu dla konfiguracji Matplotlib
RUN mkdir -p /app/matplotlib_config
RUN chmod -R 777 /app/matplotlib_config
ENV MPLCONFIGDIR=/app/matplotlib_config

ENV QT_DEBUG_PLUGINS=1
ENV QT_QPA_PLATFORM=xcb
ENV QT_QPA_PLATFORM_PLUGIN_PATH=/opt/Qt/${QT_VERSION}/gcc_64/plugins
ENV QT_PLUGIN_PATH=/opt/Qt/${QT_VERSION}/gcc_64/plugins
ENV DISPLAY=:1

# Aktualizacja pip i instalacja zależności Pythona
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
