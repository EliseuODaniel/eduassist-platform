ARG NODE_BASE_IMAGE=node:24-bookworm-slim

FROM ${NODE_BASE_IMAGE} AS deps

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

COPY apps/admin-web/package.json ./
COPY apps/admin-web/package-lock.json ./
RUN npm ci

FROM deps AS builder

COPY apps/admin-web ./
RUN npm run build

FROM ${NODE_BASE_IMAGE} AS runner

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/app ./app
COPY --from=builder /app/lib ./lib
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000

CMD ["npm", "run", "start"]
