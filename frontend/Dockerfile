# Produktions-Image des Frontends: erst die SPA bauen, dann statisch per nginx
# ausliefern (mit /api- und /karte-Proxy - same-origin wie im Dev).
# Baukontext ist das Projektwurzelverzeichnis (docker-compose.prod.yml, .dockerignore), damit version.json als
# einzige Quelle der Fassung mitkommt.
FROM node:20-alpine AS build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
# vite.config.ts liest ../version.json und baut die Fassung ein
COPY version.json /app/version.json
COPY telefon-katalog.json /app/telefon-katalog.json
RUN npm run build

FROM nginx:alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
EXPOSE 80
