# Feature Branch Plan — X3r0Day API Sniffer

This document outlines a phased rollout strategy. Each phase represents a feature branch that can be developed, reviewed, and merged independently.

---

## Phase 1: Foundation & Tooling
**Branch:** `phase/1-tooling-foundation`
**Goal:** Establish modern Python project standards, linting, and CI.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 1.1 Add `pyproject.toml` with project metadata, dependencies, and tool config | `pyproject.toml`, `requirements.txt` (deprecate) | Small |
| 1.2 Configure Ruff (lint + format + isort) | `pyproject.toml` (ruff section) | Small |
| 1.3 Configure mypy (strict) with per-module overrides | `pyproject.toml` (mypy section) | Small |
| 1.4 Add `.editorconfig` | `.editorconfig` | Small |
| 1.5 Add `.pre-commit-config.yaml` | `.pre-commit-config.yaml` | Small |
| 1.6 Create `docs/` directory (move README diagrams here) | `docs/` | Small |
| 1.7 Add `__version__` to package | `src/__init__.py` or `src/_version.py` | Tiny |
| 1.8 Initial `CHANGELOG.md` | `CHANGELOG.md` | Tiny |

**Verification:** `ruff check .`, `mypy src/`, `pre-commit run --all-files`

---

## Phase 2: Testing Infrastructure
**Branch:** `phase/2-test-infrastructure`
**Goal:** Set up pytest framework, fixtures, and initial test suite for core modules.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 2.1 Install pytest, pytest-cov, pytest-mock | `pyproject.toml` | Tiny |
| 2.2 Create `tests/` directory structure | `tests/`, `tests/conftest.py` | Small |
| 2.3 Add shared test fixtures (sample signatures, mock repo data, mock Groq client) | `tests/conftest.py`, `tests/fixtures/` | Medium |
| 2.4 Unit tests for `signature_loader.py` | `tests/test_signature_loader.py` | Small |
| 2.5 Unit tests for `scanner_matcher.py` (regex matching, false positives, normalization) | `tests/test_scanner_matcher.py` | Medium |
| 2.6 Unit tests for `scanner_targets.py` | `tests/test_scanner_targets.py` | Medium |
| 2.7 Unit tests for `category_routing.py` | `tests/test_category_routing.py` | Small |
| 2.8 Unit tests for `scanner_io.py` (atomic JSON) | `tests/test_scanner_io.py` | Small |
| 2.9 Unit tests for `ai_client.py` (retries, JSON salvage) | `tests/test_ai_client.py` | Medium |

**Verification:** `pytest --cov=src tests/` — target > 80% coverage on tested modules

---

## Phase 3: CI/CD Pipeline
**Branch:** `phase/3-ci-cd`
**Goal:** GitHub Actions workflows for quality gates, testing, and security.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 3.1 Workflow: lint + type-check on PR/push | `.github/workflows/quality.yml` | Small |
| 3.2 Workflow: test matrix (3.8–3.12) with coverage gate | `.github/workflows/test.yml` | Small |
| 3.3 Workflow: security scan (bandit + trufflehog) | `.github/workflows/security.yml` | Small |
| 3.4 Dependabot config for pip + GitHub Actions | `.github/dependabot.yml` | Tiny |

**Verification:** Push to branch, verify all actions pass

---

## Phase 4: Docker & Deployment
**Branch:** `phase/4-docker-deploy`
**Goal:** Reproducible Docker image for headless/server deployment.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 4.1 Multi-stage Dockerfile (slim Python image) | `Dockerfile` | Medium |
| 4.2 `.dockerignore` | `.dockerignore` | Tiny |
| 4.3 `docker-compose.yml` for local dev | `docker-compose.yml` | Small |
| 4.4 CI workflow: build + push Docker image to ghcr.io | `.github/workflows/docker.yml` | Medium |
| 4.5 Health check endpoint (`/health` simple HTTP server) | `src/health.py` (new) | Small |

**Verification:** `docker build -t api-sniffer . && docker run api-sniffer`

---

## Phase 5: Security Hardening
**Branch:** `phase/5-security-hardening`
**Goal:** Address security concerns from the audit.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 5.1 Add `.env.example` | `.env.example` | Tiny |
| 5.2 Add input validation for repo URLs (sanitize before subprocess) | `src/scanner/scanner_archive.py`, `src/shared/scanner_targets.py` | Medium |
| 5.3 Add `shutil.which('git')` check before subprocess calls | `src/scanner/scanner_archive.py` | Small |
| 5.4 API key validation (syntax check on GitHub token, Groq key) | `src/scanner/scanner_token.py`, `src/shared/ai_client.py` | Small |
| 5.5 Adaptive rate-limit backoff in APISniffer | `src/APISniffer.py` | Medium |
| 5.6 Review `warnings.filterwarnings("ignore")` — scope it tightly | `src/shared/requests_compat.py` | Tiny |
| 5.7 Bandit configuration in `pyproject.toml` | `pyproject.toml` | Tiny |

**Verification:** `bandit -r src/`, manual review of subprocess calls

---

## Phase 6: Documentation & Licensing
**Branch:** `phase/6-docs-license`
**Goal:** Complete project documentation and choose an OSI-approved license.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 6.1 Add LICENSE file (MIT recommended) | `LICENSE` | Tiny |
| 6.2 Create `CONTRIBUTING.md` | `CONTRIBUTING.md` | Small |
| 6.3 Create `SECURITY.md` (disclosure policy) | `SECURITY.md` | Small |
| 6.4 Expand README with full CLI reference | `README.md` | Medium |
| 6.5 Add architecture diagram | `docs/architecture.md` | Medium |
| 6.6 Create `docs/cli-reference.md` | `docs/cli-reference.md` | Small |
| 6.7 Create `docs/environment-variables.md` | `docs/environment-variables.md` | Small |

**Verification:** Review rendered Markdown

---

## Phase 7: Error Handling & Resilience
**Branch:** `phase/7-error-handling`
**Goal:** Graceful degradation, retry logic, and data integrity guarantees.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 7.1 Global exception hook (`sys.excepthook`) | `main.py` or new `src/exceptions.py` | Small |
| 7.2 Exponential backoff in network retries | `src/scanner/scanner_network.py`, `src/APISniffer.py` | Medium |
| 7.3 JSON file corruption detection (try/except on load) | `src/scanner/scanner_io.py`, `src/shared/ai_search_runtime.py` | Small |
| 7.4 Graceful fallback when Groq API is down | `src/AIWorkflow.py`, `src/AISearch.py` | Medium |
| 7.5 Timeout enforcement on all HTTP calls | `src/shared/ai_client.py`, `src/scanner/scanner_network.py` | Small |
| 7.6 Graceful shutdown with timeout (SIGTERM → finish current task → exit) | `src/scanner/scanner_signals.py` | Small |

**Verification:** Kill process mid-scan, verify data integrity

---

## Phase 8: Operations & Observability
**Branch:** `phase/8-operations`
**Goal:** Structured logging, data management, and notifications.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 8.1 Replace `print()` with structured logging (structlog or stdlib logging + JSON) | All modules | Large |
| 8.2 Log-to-file option (`--log-file`) | `src/scanner/scanner_args.py`, new `src/logging_setup.py` | Medium |
| 8.3 Dry-run mode (`--dry-run`, preview without saving) | `main.py`, `src/scanner/scanner_args.py` | Medium |
| 8.4 Data retention: `--max-age` flag to purge old findings | `src/scanner/scanner_args.py`, `src/scanner/scanner_io.py` | Small |
| 8.5 Optional webhook notification on new high-severity findings | New `src/notifier.py` | Medium |
| 8.6 Disk space check before archive download | `src/scanner/scanner_network.py` or `scanner_archive.py` | Small |

**Verification:** Run with `--log-file scan.log --dry-run`

---

## Phase 9: Performance & Advanced Features
**Branch:** `phase/9-performance`
**Goal:** Scale up discovery and scanning throughput.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 9.1 API call pacing / rate-limit bucket | `src/APISniffer.py` | Medium |
| 9.2 Streaming JSON reader/writer for large datasets | `src/scanner/scanner_io.py` | Medium |
| 9.3 Multi-token rotation for GitHub API discovery | `src/APISniffer.py`, `src/scanner/scanner_token.py` | Large |
| 9.4 Configurable file extension whitelist/blacklist | `src/scanner/scanner_archive.py`, `src/scanner/scanner_args.py` | Small |
| 9.5 Parallel repo scanning (multi-process or asyncio) | `src/APIScanner.py`, `src/scanner/scanner_archive.py` | Large |

**Verification:** Benchmark against current single-threaded baseline

---

## Phase 10: Feature Completion
**Branch:** `phase/10-feature-complete`
**Goal:** Final polish — the last mile before v1.0.

| Task | Files Affected | Effort |
|------|---------------|--------|
| 10.1 Remove all bare `except:` clauses | All modules | Small |
| 10.2 Consistent type hints across entire codebase | All modules | Large |
| 10.3 Remove dead code / commented-out blocks | All modules | Medium |
| 10.4 Consistent error message format | All modules | Medium |
| 10.5 Add `--version` flag | `main.py` | Tiny |
| 10.6 Final review: remove any `TODO` / `FIXME` / `HACK` | All modules | Medium |
| 10.7 Tag v1.0.0 | git tag | Tiny |

**Verification:** Full pipeline test, code freeze, release

---

## Dependency Graph

```
Phase 1 (Tooling)
   │
   ▼
Phase 2 (Tests) ──► Phase 3 (CI/CD)
   │                     │
   ▼                     ▼
Phase 5 (Security)   Phase 4 (Docker)
   │                     │
   ▼                     │
Phase 6 (Docs) ◄────────┘
   │
   ▼
Phase 7 (Error Handling)
   │
   ▼
Phase 8 (Operations)
   │
   ▼
Phase 9 (Performance)
   │
   ▼
Phase 10 (Feature Complete → v1.0)
```

Phases 4 and 5 are independent of each other and can be parallelized.
Phase 6 depends on Phase 5 (for updated docs on security) but can start early.
