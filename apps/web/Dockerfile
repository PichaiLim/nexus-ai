FROM node:24.22.3-bookworm-slim AS build
WORKDIR /repo/apps/web
ENV NEXT_TELEMETRY_DISABLED=1
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web .
COPY docs/nexus-ai-codex-handoff/nexus-ai-mockup.html /repo/docs/nexus-ai-codex-handoff/
ARG NEXUS_API_ORIGIN=http://api:8000
RUN npm run build && npm prune --omit=dev --no-audit --no-fund

FROM node:24.22.3-bookworm-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY --from=build --chown=node:node /repo/apps/web/.next ./.next
COPY --from=build /repo/apps/web/node_modules ./node_modules
COPY --from=build /repo/apps/web/package.json ./package.json
USER node
EXPOSE 3000
CMD ["node", "node_modules/next/dist/bin/next", "start", "--hostname", "0.0.0.0"]
