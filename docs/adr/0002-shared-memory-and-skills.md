# Workspace memory and skills

Status: PostgreSQL and authenticated API foundation implemented and verified on Docker. UI, MCP, and project-level sharing remain planned.

## Shared access

Nexus AI will manage Memory and Skills centrally within each workspace. Agents can reuse approved records across runtimes. External AI clients can read the same records through authenticated API or MCP calls. Both entry points enforce the same workspace, project, and record permissions on the server.

| Registry | Purpose | Initial read operations |
|---|---|---|
| Memory | Project facts, decisions, and handoff context | `memory.recall` |
| Skills | Reusable instructions and workflows, such as the Nexus AI UI spacing audit | `skills.list`, `skills.get` |

PostgreSQL will hold records, ownership, and access metadata. New records start private. Authorized owners can selectively publish them to a project or workspace. When importing memory from another client, share an approved summary and keep private source history in its original scope.

## Skill publishing

- Give each skill a stable ID and version. Record its owner, scope, source, instructions, and required tools.
- Allow authorized contributors to draft skills. Require a separate publish permission to make a version available to other agents. Support version pinning and withdrawal.
- Validate the workspace and record permissions before listing or returning a skill. Audit publishes, withdrawals, and access decisions.
- Treat imported skills as untrusted content. A skill may declare required tool permissions. The agent's existing grants and approval rules govern every invocation.

## First delivery

Start with owner-managed records and read-only access for agents. Verify access with two agents in one workspace and a caller in another workspace. Add shared editing, script execution, and broader publishing only through their own permission and verification work.

Phase 3A uses workspace-level publication with private drafts. Owners can edit and delete memory records, and Skills use immutable numbered versions. Phase 3B adds narrower project grants and separate contributor and publisher roles. Track both milestones in the [development roadmap](../development-roadmap.md).
