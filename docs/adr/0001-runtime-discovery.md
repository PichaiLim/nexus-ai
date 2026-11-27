# Read-only discovery through runtime adapters

Phase 1A supports Ollama and LM Studio through the same Model Sources API. The web app reads the source list and requests test or sync actions by source ID. The API resolves those IDs from server configuration, and each adapter reports only the states its runtime provides.

Model identity combines source ID and native model ID. Installed, loaded, and served are distinct nullable fields. An adapter with only a served-model endpoint can report served status while leaving installed and loaded unknown.

Configured origins act as the destination allowlist. Redirects and environment proxies are disabled. A credential reference can point to a runtime token held in an environment variable. Test Connection checks compatibility without replacing the last successful snapshot. Sync serializes requests per source and preserves the last successful result when a source fails.

Phase 1A runs locally with one API process. Source configuration is loaded at startup and snapshots live in that process. Durable registry storage, interactive source management and network deployment require subsequent work.
