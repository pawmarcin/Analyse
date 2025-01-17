# Użyj obrazu bazowego
FROM python:3.9

# Zainstaluj git
RUN apt-get update && apt-get install -y git

# Sklonuj repozytorium
RUN git clone https://github.com/pawmarcin/Analyse.git /app

# Ustaw katalog roboczy
WORKDIR /app

# Zainstaluj zależności
RUN pip install -r requirements.txt

# Ustaw punkt wejścia
ENTRYPOINT ["python", "main.py"]
