ARG NODE_BASE_IMAGE=node:24-bookworm-slim
FROM ${NODE_BASE_IMAGE}

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

COPY apps/admin-web/package.json ./
RUN npm install

COPY apps/admin-web ./

EXPOSE 3000

CMD ["npm", "run", "dev"]

