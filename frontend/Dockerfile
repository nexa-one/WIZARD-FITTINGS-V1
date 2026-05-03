# CFM Fittings Pro – Frontend Dockerfile
FROM node:20-alpine AS base

WORKDIR /app

COPY package*.json ./

# ─── Development Stage ────────────────────────────────────────────────────────
FROM base AS development

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ─── Build Stage ─────────────────────────────────────────────────────────────
FROM base AS builder

RUN npm ci

COPY . .
RUN npm run build

# ─── Production Stage ─────────────────────────────────────────────────────────
FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
