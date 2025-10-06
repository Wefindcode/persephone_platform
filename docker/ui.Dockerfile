# syntax=docker/dockerfile:1.4

ARG NEXT_PUBLIC_API_BASE=http://localhost:8000

FROM node:18-bullseye AS base
WORKDIR /app
ARG NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_API_BASE=${NEXT_PUBLIC_API_BASE}

FROM base AS deps
COPY apps/ui/package*.json ./
RUN npm install --no-audit --progress=false

FROM base AS builder
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY apps/ui/ ./
RUN npm run build && npm prune --omit=dev

FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY apps/ui/package*.json ./

EXPOSE 3000
CMD ["npm", "run", "start"]
