# Repository Guidelines

## Project Structure

Nexus AI is a self-hosted, local-first AI platform. The web app lives in `apps/web`, the FastAPI package in `apps/api/nexus_ai`, and integration tests in `tests/integration`. The original prototype is in `docs/nexus-ai-codex-handoff`. When introducing a module, document its location and entry point in the README.

## Development and Verification

Follow the README for local startup, the Python integration suite, and web builds and type checks. For documentation changes, review rendered Markdown and check relative links. Run `git diff --check` and review staged files with `git diff --cached --check`.

## Writing and Coding Style

Use descriptive Markdown headings, backticks for paths and commands, and fenced blocks for multiline examples. Preserve established terms such as Nexus AI and MCP. There is no repository-wide code formatter or indentation convention yet. When introducing a language, document its formatting and naming conventions alongside its development commands.

## Testing

Python integration tests use `unittest` and the `test_*.py` naming convention. Use HTTPX mock transports to exercise the API with deterministic runtime responses. When introducing executable behavior, include a repeatable check for its main entry point and document how to run it.

## Commits and Pull Requests

Use concise, imperative commit subjects with the prefixes in the Git & Version Control Standards, such as `docs: revise README`. In pull requests, summarize the change and list what you verified. Link a related issue when one exists, and include screenshots when a change affects a visible interface. Keep the README accurate about which capabilities are available and which are planned.

## Git & Version Control Standards

- **Scoped & Atomic Changes:** Keep changes strictly scoped to the requested task. Avoid unrequested edits to unrelated files, lockfiles, or formatting across untouched code.
- **Inspect Diff Before Finishing:** Always review modified files and diffs before concluding a task; remove temporary debug statements, unused imports, or unintended test artifacts.
- **No Secrets or Artifacts in Git:** Never stage or commit `.env` files, credentials, API keys, tokens, build outputs, or large binary/data dumps.
- **Clear Commit & Branch Intent:** When proposing commit messages or branches, use clear prefixes (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`) and keep each change focused on a single concern.
- **Safe Rollback & Migration Discipline:** Keep database migrations and breaking changes backward-compatible or clearly isolated so individual commits or releases can be reverted safely.

## Engineering, Quality & Regression-Safe Standards

Follow these rules strictly when writing, editing, or reviewing code in this repository.

### 1. Change Safety & Regression Prevention (CRITICAL)

- **Impact Analysis First:** Before modifying any shared function, component, API contract, or database schema, trace all callers, consumers, and dependent tests across the codebase.
- **Minimal, Scoped Diffs:** Change only what is required for the task. Never perform unrelated refactoring, formatting sweeps, or logic rewrites in the same change.
- **Backward Compatibility:** Prefer additive changes (new optional fields, new endpoints, new migration columns). Never break existing API payloads, function signatures, or database columns without migrating all consumers and updating tests in the same change.
- **Protect Existing Tests:** Never delete, skip, or weaken assertions in existing tests just to make the test suite pass. If behavior intentionally changes, explain why and update tests accurately.
- **Bug-Fix Rule:** Every bug fix must include a regression test that reproduces the original bug and fails before the fix.

### 2. Architecture & Code Quality

- Separate business logic/services from UI components, API handlers, and database queries.
- Use strict typing (`strict: true` in TypeScript, type annotations in Python); avoid `any` and silent linter suppressions.
- Handle errors explicitly with timeouts/retries for external calls; never swallow exceptions or expose stack traces in responses.
- Keep functions small, modular, and free of duplicated business rules.

### 3. Web UI & Accessibility (WCAG 2.2 AA)

- Prefer semantic HTML (`<main>`, `<nav>`, `<button>`, `<label>`, `<dialog>`) over custom ARIA roles.
- Keep text contrast at least 4.5:1 for normal text and 3:1 for large text or UI borders/controls.
- Ensure full keyboard navigation with visible `:focus-visible` styles and touch targets of at least 44x44px.
- Style all interactive states (`default`, `hover`, `focus-visible`, `active`, `disabled`, `loading`, `error`).
- Use mobile-first responsive layouts, `clamp()` fluid sizing, and centralized design tokens. Preserve the handoff mockup's spacing for shared elements such as the content container, page headings, and cards. Use an 8px spacing scale for new elements without a reference in the mockup.
- When changing shared layout, compare the rendered spacing with the handoff using the Playwright workspace spacing tests. Review intentional design changes before updating the baseline.
- Reserve dimensions/aspect ratios on media to prevent layout shift (CLS), keep interactions responsive, and respect `prefers-reduced-motion`.

### 4. Software Testing

- Structure tests using Arrange-Act-Assert (AAA) with clear names describing behavior.
- Balance Unit (isolated/mocked), Integration (DB/API/auth), and E2E (critical user flows using accessible locators) tests.
- Test boundary values, empty/null inputs, invalid payloads, permission errors, and failure states—not just happy paths.
- Assert concrete outcomes (state, database changes, status codes, error payloads) and keep tests deterministic.

### 5. Security (OWASP Top 10)

- Enforce authentication and object-level authorization on every protected backend route; never trust client-side checks alone.
- Validate and sanitize all inputs, query params, and uploads on the backend.
- Use parameterized queries/ORM bindings only; prevent XSS, CSRF, and overly permissive CORS.
- Never hardcode secrets, API keys, or tokens in code; load configuration from environment variables.

### 6. API, Database & DevOps

- Keep REST endpoints, HTTP status codes, pagination, and JSON error payloads consistent.
- Manage schema changes via reversible migrations with database constraints (`NOT NULL`, `UNIQUE`, `CHECK`, foreign keys) and indexes for frequent queries/joins.
- Offload slow tasks to background workers/queues and wrap multi-step writes in transactions.
- Maintain reproducible container builds (`Dockerfile` / `docker-compose.yml`), structured JSON logs without secrets/PII, and `/health` endpoints.

#### Docker & Container Standards

- **Multi-Stage & Minimal Images:** Use multi-stage Docker builds with pinned image tags (avoid untagged `latest`), non-root runtime users, and a comprehensive `.dockerignore`.
- **Healthchecks & Startup Order:** Define healthchecks for databases, caches, and services. Gate dependent containers on `service_healthy`.
- **Env & Secret Safety:** Pass runtime configuration via `.env` and use orchestrator secrets where available. Keep secrets and `.env` files out of Docker images.
- **Resource & Lifecycle Hygiene:** Set memory and CPU limits where appropriate for production services, handle `SIGTERM` for graceful shutdown, and clean up temporary test containers and volumes after test runs.

### 7. Mandatory Verification Before Finishing

- Run the **full** relevant test suite (not just new tests), linters, and type-checkers after every change.
- If shared code, auth, database schema, or core flows were touched, verify end-to-end/integration tests for existing features before reporting completion.

### 8. RAG & Knowledge Retrieval Standards

- **Structure-Aware Chunking:** Chunk documents along semantic/structural boundaries (headings, sections, paragraphs) with parent title context and metadata rather than naive fixed-character splits.
- **Document Lifecycle:** Use stable document IDs and track source versions. Make ingestion idempotent so retries of the same version do not create duplicate chunks. Propagate updates, deletions, and permission changes to vector and lexical indexes and invalidate affected caches. Prevent stale or revoked content from being served while propagation is pending.
- **Hybrid Retrieval & Filtering:** Combine vector similarity with keyword/lexical search (BM25) and enforce strict metadata filters (`tenant_id`, access permissions, active status) at query time—never post-filter sensitive data in the LLM prompt.
- **End-to-End Authorization:** Enforce current tenant and document permissions server-side during retrieval, on cache reads, and when opening cited sources. Scope caches by tenant and access context. Add regression tests for cross-tenant access and permission revocation after caching.
- **Local and Cloud Data Boundaries:** Define which documents may be sent to external embedding providers, rerankers, or LLMs. Enforce that policy before sending document text, chunks, or derived context. Block external calls for local-only requests and preserve that restriction during provider fallback.
- **Reranking & Context Budget:** Retrieve broad candidates, rerank for relevance, and inject only top-scoring chunks within a bounded token budget to prevent lost-in-the-middle degradation.
- **Grounded Generation & Citations:** Instruct the model to answer strictly from retrieved context, cite source identifiers, and explicitly abstain when evidence is insufficient.
- **Prompt Injection Isolation:** Delimit retrieved chunks clearly from system instructions and treat all retrieved text as untrusted data.
- **RAG Regression Evaluation:** Maintain a golden Q&A evaluation dataset to measure retrieval recall and answer faithfulness whenever chunking, embeddings, or retrieval logic changes.
