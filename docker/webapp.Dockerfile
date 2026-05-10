FROM node:24.9.0-bookworm-slim

WORKDIR /workspace/webapp

RUN corepack enable \
    && corepack prepare npm@11.6.0 --activate

COPY webapp/package.json webapp/package-lock.json ./
RUN npm ci

COPY webapp/ ./

CMD ["sh", "-lc", "npm test && npm run build"]
