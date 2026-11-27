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

## Phase 1A development

The Nexus workspace uses the navigation and theme from the handoff mockup. Open **Model Studio → Model Sources** to inspect Ollama and LM Studio inventories and loaded state. Model Sources starts in Demo mode. Toggle **Live** to query configured runtimes while other workspace pages continue to display their demo state. The standalone handoff remains available at `/demo`. Source snapshots reset on API restart.

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

## Vision

Build a personal AI ecosystem where models, agents, tools, knowledge, and computing resources work together under the user's control.

Your models. Your tools. Your data. Your intelligence.
