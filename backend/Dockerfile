# Produktions-Image des Backends. Mehrstufig: bauen mit Build-Werkzeugen,
# schlankes Laufzeit-Image ohne Compiler.
FROM python:3.12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
COPY --from=build /install /usr/local
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "wetterwarte.main:app", "--host", "0.0.0.0", "--port", "8000"]
