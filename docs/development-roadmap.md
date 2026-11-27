# Nexus AI development roadmap

This roadmap tracks implementation. The [project handoff](nexus-ai-codex-handoff/NEXUS_AI_PROJECT.md) records the original requirements and phase gates.

| Milestone | Status | Exit criteria |
|---|---|---|
| Phase 0 and 1A · Docker and model discovery | Implemented | Demo workspace and read-only discovery for Ollama and LM Studio on Docker |
| Localization · Thai UI foundation | Implemented and verified on Docker | Thai and English switcher, translated navigation, Overview, and Model Sources with mobile coverage. Shared Memory supports saving and literal search in Thai. |
| Phase 1B · Core chat and MCP | Planned | Local streaming chat, authenticated and scoped MCP tools, and auditable access |
| Phase 2 · Multi-agent orchestration | Planned | Bounded delegation, cancellation, checkpoints, and approval handling |
| Phase 3A · Shared Memory and Skills foundation | Implemented and verified on Docker | PostgreSQL-backed records, owner publishing, versioned Skills, and authenticated API reads with workspace isolation |
| Phase 3B · Memory Center, Skills UI, and MCP access | Planned | Live UI management, MCP read tools for approved clients, project-level sharing, and separate publishing permissions |
| Phase 3C · Knowledge retrieval | Planned | Thai and document retrieval, citations, deletion propagation, and retrieval regression evaluation |
| Phases 4–6 · Hardening and expansion | Planned | Backup and restore, security verification, automation, benchmarking, and distributed workers |

The Phase 3A foundation can advance alongside Phase 1B and Phase 2. Phase 3B MCP access depends on the authenticated gateway. The [shared memory and skills ADR](adr/0002-shared-memory-and-skills.md) describes the access model.

Extend Thai labels and messages as the remaining demo pages become live. Phase 3C includes Thai content retrieval and citation evaluation.
