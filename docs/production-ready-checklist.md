# Production-Ready Checklist — X3r0Day API Sniffer

## 1. Testing & Quality Assurance

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.1 | Unit tests for `scanner_matcher.py` (regex engine, false-positive filtering, normalization) | ❌ | 422 lines, highest-risk module |
| 1.2 | Unit tests for `signature_loader.py` (pattern compilation, Heroku filtering) | ❌ | Core signature pipeline |
| 1.3 | Unit tests for `scanner_targets.py` (URL/AI-based repo extraction, dedup) | ❌ | Used by live injection |
| 1.4 | Unit tests for `category_routing.py` (tokenizer, category inference) | ❌ | 186 lines, query planning dependency |
| 1.5 | Unit tests for `ai_search_runtime.py` (query planning, result rendering) | ❌ | 497 lines, complex logic |
| 1.6 | Unit tests for `scanner_network.py` (download, proxy fallback, size limits) | ❌ | Network I/O critical path |
| 1.7 | Unit tests for `scanner_io.py` (atomic JSON, thread-safe append/remove) | ❌ | Data integrity critical |
| 1.8 | Unit tests for `scanner_archive.py` (ZIP/TAR/git clone extraction) | ❌ | Archive parsing edge cases |
| 1.9 | Unit tests for `ai_client.py` (retry logic, JSON salvage) | ❌ | LLM integration reliability |
| 1.10 | Integration test: discovery → scanner → search pipeline | ❌ | End-to-end workflow |
| 1.11 | Integration test: AI workflow orchestrator routing | ❌ | NL routing correctness |
| 1.12 | Test coverage target configured (pytest-cov) | ❌ | Enforce >= 80% |

## 2. Build & Packaging

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.1 | `pyproject.toml` with project metadata | ✅ | Modern Python packaging |
| 2.2 | `setup.cfg` or `setup.py` fallback | ❌ | For legacy pip compatibility |
| 2.3 | Version string (`__version__` in package `__init__.py`) | ❌ | Single source of truth |
| 2.4 | Lockfile (`requirements.lock` or `pip freeze` snapshot) | ✅ | Deterministic installs |
| 2.5 | Dockerfile (multi-stage, slim image) | ✅ | Reproducible deployment |
| 2.6 | `.dockerignore` | ✅ | Exclude dev artifacts from image |
| 2.7 | Docker Compose for local dev (optional) | ❌ | Quick start for contributors |
| 2.8 | Python version classifier in `pyproject.toml` | ❌ | Currently implicit >= 3.8 |

## 3. CI/CD

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.1 | GitHub Actions: lint on PR/push | ❌ | ruff or flake8 |
| 3.2 | GitHub Actions: type-check on PR/push | ❌ | mypy with strict config |
| 3.3 | GitHub Actions: test on PR/push (matrix: 3.8–3.12) | ❌ | pytest |
| 3.4 | GitHub Actions: coverage gate | ❌ | Fail if coverage drops |
| 3.5 | GitHub Actions: Docker image build + push | ❌ | ghcr.io registry |
| 3.6 | GitHub Actions: security scan (bandit / trufflehog) | ❌ | SAST for secret leaks |
| 3.7 | Dependabot / Renovate for dependency updates | ❌ | Automated maintenance |
| 3.8 | Pre-commit hook config (`.pre-commit-config.yaml`) | ✅ | Local quality gates |

## 4. Code Quality & Linting

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.1 | Ruff or flake8 configuration | ❌ | Enforce PEP 8 |
| 4.2 | Black or Ruff formatter config | ❌ | Consistent formatting |
| 4.3 | isort config (import ordering) | ❌ | Standardized imports |
| 4.4 | mypy strict mode configuration | ❌ | Gradual typing enforcement |
| 4.5 | EditorConfig (`.editorconfig`) | ❌ | Cross-editor consistency |
| 4.6 | Pre-commit hooks (lint, format, type-check) | ❌ | Catch issues before commit |
| 4.7 | Docstring convention (Google or NumPy style) | ❌ | Currently no docstrings |
| 4.8 | Remove unused imports / dead code | ❌ | Audit all modules |

## 5. Security

| # | Item | Status | Notes |
|---|------|--------|-------|
| 5.1 | `.env.example` documenting all required env vars | ❌ | GROQ_API_KEY, GITHUB_TOKEN, etc. |
| 5.2 | Remove or justify `warnings.filterwarnings("ignore")` in `requests_compat.py` | ⚠️ | Suppresses all requests warnings |
| 5.3 | Input validation for all user-supplied repo names/URLs | ⚠️ | Used in subprocess git clone |
| 5.4 | Rate-limit awareness and adaptive backoff in `APISniffer.py` | ⚠️ | Hardcoded 2s sleeps, no adaptive |
| 5.5 | API key validation on input (syntax check before use) | ❌ | Invalid keys cause runtime errors |
| 5.6 | Secret masking in `leaked_keys.json` output (configurable) | ⚠️ | masked in display, full in file |
| 5.7 | Bandit security linter integration | ❌ | Catch common vulnerabilities |
| 5.8 | Audit subprocess calls for injection vectors | ❌ | git clone with user input |
| 5.9 | Consider `shutil.which('git')` check before subprocess calls | ❌ | Better error messages |

## 6. Documentation

| # | Item | Status | Notes |
|---|------|--------|-------|
| 6.1 | LICENSE file (MIT / Apache 2.0 / GPL) | ❌ | README mentions terms but no file |
| 6.2 | CONTRIBUTING.md | ❌ | How to contribute, code standards |
| 6.3 | CHANGELOG.md | ❌ | Keep a release log |
| 6.4 | SECURITY.md (responsible disclosure policy) | ❌ | Security researchers expect this |
| 6.5 | API reference / module docs | ❌ | Auto-generated or manual |
| 6.6 | Quickstart in README (copy-paste usable) | ✅ | Existing README covers basics |
| 6.7 | Architecture diagram / flow in docs | ❌ | Visualize pipeline stages |
| 6.8 | Document all CLI flags and env vars | ❌ | Some flags undocumented |

## 7. Operations & Monitoring

| # | Item | Status | Notes |
|---|------|--------|-------|
| 7.1 | Structured logging (JSON logs) | ❌ | Currently Rich TUI + print |
| 7.2 | Log rotation or file output option | ❌ | For headless/server runs |
| 7.3 | Graceful shutdown timeout enforcement | ⚠️ | Signal handlers exist but no timeout |
| 7.4 | Health check endpoint / heartbeat (for Docker) | ❌ | Container orchestration |
| 7.5 | Configurable data retention (auto-clean old findings) | ❌ | leaked_keys.json grows unbounded |
| 7.6 | Notification hooks (webhook, email, Slack) | ❌ | Alert on critical findings |
| 7.7 | Dry-run / audit mode (no destructive writes) | ❌ | Preview before scanning |

## 8. Error Handling & Resilience

| # | Item | Status | Notes |
|---|------|--------|-------|
| 8.1 | Global exception handler for uncaught errors | ❌ | Crashes on unexpected exceptions |
| 8.2 | Retry with exponential backoff in network calls | ⚠️ | Limited retry, no backoff |
| 8.3 | File corruption detection for JSON data files | ❌ | Corrupt file = data loss |
| 8.4 | Graceful degradation when AI/LLM unavailable | ❌ | Workflow hard-fails without Groq |
| 8.5 | Timeout enforcement on all external calls | ⚠️ | Partially implemented |
| 8.6 | Disk space check before downloading archives | ❌ | Unbounded download growth |

## 9. Performance & Scalability

| # | Item | Status | Notes |
|---|------|--------|-------|
| 9.1 | Configurable concurrency (max threads) | ✅ | `--max-threads` flag |
| 9.2 | Throttle/rate-limit per second on GitHub API | ❌ | No API call pacing |
| 9.3 | Streaming JSON writer for large result sets | ❌ | Loads entire file into memory |
| 9.4 | Cache compiled regex patterns across scans | ✅ | Already cached |
| 9.5 | Parallel repo discovery (multi-token rotation) | ❌ | Single GITHUB_TOKEN |
| 9.6 | File size limit for scanned files | ✅ | Existing limit in scanner |

## 10. Legal & Compliance

| # | Item | Status | Notes |
|---|------|--------|-------|
| 10.1 | LICENSE file with OSI-approved license | ❌ | Must choose one |
| 10.2 | Terms of use / disclaimer in README | ⚠️ | Mentions "responsible disclosure" only |
| 10.3 | Rate-limit compliance with GitHub ToS | ⚠️ | Uses search API, should verify ToS |
| 10.4 | Data privacy: option to delete local findings | ❌ | No clean/expire command |

## Legend

- ✅ = Implemented
- ⚠️ = Partial / needs improvement
- ❌ = Missing / not started
