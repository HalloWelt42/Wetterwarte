# Produktions-Image des Backends. Mehrstufig: bauen mit Build-Werkzeugen,
# schlankes Laufzeit-Image ohne Compiler. Baukontext ist das Projektwurzelverzeichnis (docker-compose.prod.yml,
# .dockerignore), damit version.json als einzige Quelle der Fassung mitkommt.
FROM python:3.12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Abhängigkeiten exakt nach uv.lock: ein freies "pip install ." zieht bei jedem Bau die
# neueste Fassung (so kam eine sqlmodel-Fassung, die naive Zeitstempel ablehnt).
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /usr/local/bin/uv
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv export --frozen --no-dev --no-hashes --no-emit-project -o requirements.txt \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY backend/src ./src
RUN pip install --no-cache-dir --no-deps --prefix=/install .

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
COPY --from=build /install /usr/local
WORKDIR /app
# /api/v1/health meldet diese Fassung; die Oberfläche vergleicht ihre eingebaute damit
COPY version.json ./version.json
ENV WETTERWARTE_VERSION_DATEI=/app/version.json
# Mit der Oberfläche geteilte Dateien: Telefon-Kachelkatalog (Prüfung der Layouts), Wettercodes
COPY gemeinsam ./gemeinsam
ENV WETTERWARTE_GEMEINSAM=/app/gemeinsam
EXPOSE 8000
CMD ["uvicorn", "wetterwarte.main:app", "--host", "0.0.0.0", "--port", "8000"]
