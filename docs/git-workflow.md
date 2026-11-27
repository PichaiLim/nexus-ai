# Git workflow

Use `main` as the integration branch and a short-lived branch for each change. Open a pull request to `main`, review the diff and CI results, then merge. Use a squash merge when the branch contains follow-up or work-in-progress commits.

## Start and commit a change

From a clean working tree, update `main` and create a branch with a descriptive name.

```powershell
git switch main
git pull --ff-only origin main
git switch -c feat/local-streaming-chat
```

For changes already in progress, inspect `git status --short` and create the branch at the current commit with `git switch -c feat/describe-the-change` before updating from the remote. Keep each commit focused. Include regression tests for bug fixes and update the roadmap or ADR when a milestone or architecture decision changes.

```powershell
git status --short
git diff --check
git diff
git check-ignore -v -- .env
git add -- README.md docs/git-workflow.md
git diff --cached --check
git diff --cached
git commit -m "docs: document the Git workflow"
```

Use prefixes such as `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, and `chore:`. Review the actual staged files for local configuration, tokens, generated artifacts, and model weights before committing.

## Push and review

Run the [local verification commands](../README.md#phase-1a-development) before pushing. For registry changes, include the [PostgreSQL integration suite](../README.md#shared-memory-and-skills-api).

```powershell
git push -u origin HEAD
```

Open a PR to `main` using the repository template. CI runs on PRs targeting `main` and pushes to `main`. It checks whitespace, TypeScript, Docker builds, the API with PostgreSQL, and Playwright. The browser and source-discovery tests use fixtures so CI can run without local models. Record any live Ollama or LM Studio checks in the PR when a change affects runtime compatibility.

After merge, run `git switch main` and `git pull --ff-only origin main`. Delete the topic branch after confirming the change appears on `main`. If a shared branch needs an update from `main`, merge `origin/main` into it and resolve conflicts together.

## Release and rollback

Tag a verified commit on `main` with an annotated version tag. The first alpha can use `v0.1.0-alpha.1`. Review the commit and release notes before pushing that exact tag.

```powershell
git status --short --branch
git log -1 --oneline
git tag -a v0.1.0-alpha.1 -m "Nexus AI 0.1.0 alpha 1"
git push origin v0.1.0-alpha.1
```

Publish release notes with user-visible changes, migration or setup steps, known gaps, and verification results. To undo a merged change, create a rollback branch from current `main`, run `git revert <commit-sha>`, and open a PR for the revert. Plan database rollback and backup restoration separately when migrations have run. Assign a new tag for a corrected release.
