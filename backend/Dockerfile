# Produktions-Image des Backends. Mehrstufig: bauen mit Build-Werkzeugen,
# schlankes Laufzeit-Image ohne Compiler. Baukontext ist das Projektwurzelverzeichnis (docker-compose.prod.yml,
# .dockerignore), damit version.json als einzige Quelle der Fassung mitkommt.
FROM python:3.12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
COPY --from=build /install /usr/local
WORKDIR /app
# /api/v1/health meldet diese Fassung; die Oberfläche vergleicht ihre eingebaute damit
COPY version.json ./version.json
ENV WETTERWARTE_VERSION_DATEI=/app/version.json
EXPOSE 8000
CMD ["uvicorn", "wetterwarte.main:app", "--host", "0.0.0.0", "--port", "8000"]
