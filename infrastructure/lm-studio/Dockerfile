FROM node:24.22.3-bookworm-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl libatomic1 libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home nexus
ENV HOME=/home/nexus PATH="/home/nexus/.lmstudio/bin:$PATH"

FROM base AS build
ARG TARGETARCH
USER nexus
WORKDIR /tmp
RUN mkdir llmster-install && cd llmster-install \
    && case "$TARGETARCH" in amd64) arch=x64 ;; arm64) arch=arm64 ;; *) exit 1 ;; esac \
    && artifact="0.1.2-1-linux-$arch.full" \
    && origin="https://llmster.lmstudio.ai/download/$artifact" \
    && curl --fail --silent --show-error --location "$origin.tar.gz" --output llmster.tar.gz \
    && curl --fail --silent --show-error --location "$origin.sha512" --output llmster.sha512 \
    && printf '%s  llmster.tar.gz\n' "$(cat llmster.sha512)" | sha512sum --check \
    && tar -xzf llmster.tar.gz \
    && LMS_BOOTSTRAP_INSTALL_SH=1 ./llmster bootstrap \
    && test -x "$HOME/.lmstudio/bin/lms" \
    && mkdir -p "$HOME/.lmstudio/models"

FROM base AS runtime
COPY --from=build --chown=nexus:nexus /home/nexus /home/nexus
COPY infrastructure/lm-studio/entrypoint.sh /usr/local/bin/lm-studio-entrypoint
RUN sed -i 's/\r$//' /usr/local/bin/lm-studio-entrypoint
USER nexus
WORKDIR /home/nexus
EXPOSE 1234
ENTRYPOINT ["/bin/sh", "/usr/local/bin/lm-studio-entrypoint"]
