# Nexus AI Platform

**Connect. Think. Execute.**

Nexus AI is a self-hosted, local-first, extensible AI infrastructure platform designed to unify local AI models, cloud AI providers, autonomous multi-agent systems, bidirectional MCP connectivity, persistent memory, knowledge retrieval, automation, and distributed computing within a single ecosystem.

## Core Capabilities

- Local AI Model Discovery and Management
- Hybrid Local and Cloud AI Inference
- Bidirectional MCP Gateway
- Autonomous Multi-Agent Orchestration
- Dynamic Model Routing
- Long-term Memory and RAG
- Workflow Automation
- Model Benchmarking and Fine-tuning
- Multi-GPU and Distributed AI Cluster
- Agent-level and Tool-level Permissions
- Custom Web Management Interface
- LAN, VPN and Secure Remote Access

See the [development roadmap](docs/development-roadmap.md) and [shared Memory and Skills design](docs/adr/0002-shared-memory-and-skills.md) for implementation status and access rules.

Use the [Git workflow](docs/git-workflow.md) for branches, commits, PRs, CI checks, and release tags.

## Phase 1A development

The Nexus workspace uses the navigation and theme from the handoff mockup. Open **Model Studio → Model Sources** to inspect Ollama and LM Studio inventories and loaded state. Model Sources starts in Demo mode. Toggle **Live** to query configured runtimes while other workspace pages continue to display their demo state. The standalone handoff remains available at `/demo`. Source snapshots reset on API restart.

Use the language selector in the workspace header to switch between English and Thai. The browser remembers the choice. Thai currently covers the shared navigation, menu search, Overview, and Model Sources. Other demo pages retain their original content.

### Docker Compose

On Windows with Docker Desktop, run these commands from the repository root. Compose starts the web app, FastAPI, Ollama, and LM Studio's headless runtime (llmster). Open http://127.0.0.1:3010, go to **Model Sources**, and select **Live** to test or sync both sources. Only the web port is published, bound to loopback.

```powershell
docker compose -f compose.yaml -f compose.models.yaml up --build --wait
docker compose -f compose.yaml -f compose.models.yaml ps
```

The model override mounts the existing Windows model directories read-only. It defaults to `%USERPROFILE%/.ollama/models` and `%USERPROFILE%/.lmstudio/models`. Set `NEXUS_OLLAMA_MODELS_DIR` or `NEXUS_LM_STUDIO_MODELS_DIR` for custom directories. The Ollama directory should contain its model manifests and blobs. The LM Studio directory should contain its publisher/model folders. Model files stay in place.

For a clean start with empty Docker-managed model stores, omit the override.

```powershell
docker compose up --build --wait
```

Set `NEXUS_WEB_PORT` if port 3010 is occupied. To add or replace endpoints, set `NEXUS_MODEL_SOURCES` to the full source list. The bundled defaults resolve to `http://ollama:11434` and `http://lm-studio:1234`. For an authenticated external source, set its `token_env` to `NEXUS_SOURCE_OLLAMA_TOKEN` or `NEXUS_SOURCE_LM_STUDIO_TOKEN` and supply the corresponding environment variable to Compose.

The stack uses CPU-based discovery with Ollama `0.40.18` and llmster `0.1.2-1`. The first build fetches the images and llmster release archive. Run `docker compose down` with the same Compose files to stop the stack.

### Native development

Start the API from the repository root in PowerShell.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps/api/requirements.txt
$env:NEXUS_MODEL_SOURCES = '[{"id":"ollama","name":"Local Ollama","engine":"ollama","url":"http://127.0.0.1:11434"},{"id":"lm-studio","name":"Local LM Studio","engine":"lm-studio","url":"http://127.0.0.1:1234"}]'
.\.venv\Scripts\python.exe -m uvicorn nexus_ai.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

Enable the LM Studio server before testing it. For an authenticated source, set the source's `token_env` to a variable such as `NEXUS_SOURCE_LM_STUDIO_TOKEN` and provide its value to the API process.

In a second terminal, run `npm.cmd --prefix apps/web ci` and `npm.cmd --prefix apps/web run dev`. Open http://127.0.0.1:3000, select **Live**, and use **Test connection** or **Sync**. Keep both listeners on loopback for this development build.

If a port is occupied, select another with `--port`. For a different API port, set `NEXUS_API_ORIGIN` for the web process before starting the development server or building.

Run the integration suite and web checks from the repository root.

```powershell
$env:PYTHONPATH = 'apps/api'
.\.venv\Scripts\python.exe -m unittest discover -s tests/integration -v
npm.cmd --prefix apps/web run build
npm.cmd --prefix apps/web run typecheck
```

For the browser test, keep the web server running and use PowerShell from `apps/web`. Run `npx.cmd playwright install chromium` and `npx.cmd playwright test`. Set `NEXUS_WEB_ORIGIN` if the web server uses a nondefault port, or set `NEXUS_BROWSER_CHANNEL` to `msedge` to use installed Microsoft Edge.

Run `npx.cmd playwright test workspace-spacing` to compare the desktop and mobile layout with the original handoff at `/demo`.

## Shared Memory and Skills API

Enable the shared registry once from the repository root. The setup script adds local PostgreSQL credentials and separate owner and reader tokens to the ignored `.env` file. It preserves existing settings and does not print secret values.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\initialize-shared-registry.ps1
docker compose --profile shared -f compose.yaml -f compose.models.yaml up --build --wait
```

The Compose profile keeps PostgreSQL on a private network and stores data in the `shared-postgres` volume. Keep the existing database credentials for that volume. The app connects using the dedicated `nexus_app` role. PostgreSQL is pinned to `17.12-bookworm` and Psycopg to `3.3.9`.

Use `http://127.0.0.1:3010/api/v1/workspaces/local` with an `Authorization: Bearer <token>` header. Keep the owner token with the workspace owner. Give AI clients their own reader token. For multiple identities, configure `NEXUS_SHARED_PRINCIPALS` as an array of `workspace`, `subject`, `role`, and `token_sha256` objects.

| Action | Path under the workspace |
|---|---|
| List or search published records | `GET /memory?q=handoff` or `GET /skills?q=spacing` |
| Read an exact record or skill version | `GET /memory/{id}` or `GET /skills/{id}` |
| Create a private draft as owner | `POST /memory` or `POST /skills` with `title` and `content`. Skills also require `skill_key` and a positive integer `version` |
| Publish or withdraw as owner | `POST /{memory-or-skills}/{id}/publish` or `/withdraw` |
| Edit or delete memory as owner | `PUT /memory/{id}` or `DELETE /memory/{id}` |

Run the integration suite against the Docker database after startup.

```powershell
docker compose -f compose.yaml -f compose.models.yaml run --rm --no-deps --env NEXUS_TEST_SHARED_REGISTRY=1 --volume "${PWD}/tests/integration:/verification:ro" api python -m unittest discover -s /verification -v
```

The Memory Center remains in Demo mode. Live management UI and MCP access are listed in the [development roadmap](docs/development-roadmap.md).

## Vision

Build a personal AI ecosystem where models, agents, tools, knowledge, and computing resources work together under the user's control.

Your models. Your tools. Your data. Your intelligence.
