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
COPY gemeinsam /app/gemeinsam
RUN npm run build

FROM nginx:alpine
# Vorlage: der Start von nginx setzt die Adressen aus der Umgebung ein und legt sie als conf.d/default.conf ab
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/frontend/dist /usr/share/nginx/html
EXPOSE 80
