# Użyj obrazu bazowego
FROM python:3.9

# Zainstaluj git
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Sklonuj repozytorium
RUN git clone https://github.com/pawmarcin/Analyse.git /app

# Ustaw katalog roboczy
WORKDIR /app

# Zainstaluj zależności
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ustaw punkt wejścia
ENTRYPOINT ["python", "main.py"]
