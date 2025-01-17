FROM python:3.10-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików projektu
COPY . .

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxinerama1 \
    libxrandr2 \
    libxrender1 \
    libxtst6

# Instalacja zależności Pythona
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Utworzenie zapisywalnego katalogu
RUN mkdir -p /path/to/writable/directory
RUN chmod u+w /path/to/writable/directory

# Ustawienie zmiennej środowiskowej dla Matplotlib
ENV MPLCONFIGDIR=/path/to/writable/directory

# Uruchomienie aplikacji
CMD ["python", "main.py"]
