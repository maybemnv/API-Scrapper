# API Sniffer — Agent Guide

## Quick start
```powershell
uv sync --group dev
$env:GROQ_API_KEY="gsk_..."
uv run python main.py              # Enter = AI workflow, type "Manual" for numbered menu
uv run python src/AISearch.py --query "show all keys"   # one-shot query
```

## Entrypoints
- **`main.py`** — TUI launcher. Root `ROOT_DIR` = its parent dir. All runtime JSON files (recent_repos.json, leaked_keys.json, etc.) live there.
- **`src/APISniffer.py`** — Stage 1: GitHub repo discovery → `recent_repos.json`
- **`src/APIScanner.py`** — Stage 2: scan repos → `leaked_keys.json`, `clean_repos.json`, `failed_repos.json`
- **`src/AISearch.py`** — Stage 3: query `leaked_keys.json` via Groq AI
- **`src/AIWorkflow.py`** — NL orchestrator: routes user requests into stage(s) above

## Architecture
```
main.py
├── Enter → AIWorkflow.py  (Groq → plan → subprocess stage scripts)
└── Manual → numbered menu (subprocess each stage directly)

src/scanner/       — scanner internals (network, archive, proxy, I/O, keyboard, UI)
src/shared/        — shared logic (AI client, matcher, signatures, categories, targets)
data/signatures.json — 58 regex signatures, tagged (heroku keys gated behind --scan-heroku-keys)
config/ai_policy.json  — LLM config + workflow routing prompts (Groq, llama-3.3-70b-versatile, temp 0.1)
```

## Key conventions & quirks

### Tests / CI / packaging
- Tests live in `tests/` and run with `uv run pytest tests/ -v`.
- Dependencies live in `pyproject.toml` + `uv.lock`; use `uv sync` for local setup.
- GitHub Actions covers linting, type-checking, tests, Docker, and security scans.

### C extension auto-build
- `src/shared/scanner_matcher.py` tries to compile `fast_scanner.c` → `fast_scanner.so` at import time (needs gcc + libpcre2-8 + pkg-config). Falls back to pure Python if unavailable. Not tracked in git.

### CLI flags
- `--up-proxy` flag **or** env var `X3D_UP_PROXY=1` — persists healthy proxy pruning
- `--no-commit-history` — **disables** commit history scanning (double negation)
- `--scan-heroku-keys` — **enables** Heroku key patterns (off by default, tagged in signatures.json)
- No `--version` flag exists

### Scanner runtime controls
- `Space` — pause/resume scanning
- `I` — AI-assisted repo target injection (triggers `scanner_targets_live.py`)
- `Esc` — cancel input, `Enter` — submit target, `Ctrl+C` — shutdown

### Environment variables
| Var | Required | Notes |
|-----|----------|-------|
| `GROQ_API_KEY` | Yes (or prompted) | Used by AIWorkflow, AISearch, live target injection |
| `GITHUB_TOKEN` / `GH_TOKEN` | No | 60 req/hr unauthenticated, 5k req/hr authenticated |
| `X3D_UP_PROXY` | No | Equivalent to `--up-proxy` |
| `AI_POLICY_PATH` | No | Override `config/ai_policy.json` path |

### Runtime files (all gitignored, created in ROOT_DIR)
| File | Writer | Format |
|------|--------|--------|
| `recent_repos.json` | APISniffer | `[{name, created_at, url, stars}]` |
| `leaked_keys.json` | APIScanner | `[{repo, url, status, total_secrets, findings: [{file, line, type, secret}]}]` |
| `clean_repos.json` | APIScanner | `[{repo, url, status: "clean"}]` |
| `failed_repos.json` | APIScanner | `[{repo, status: "failed", reason}]` |
| `live_proxies.txt` | User-created | One `ip:port` per line |

### Signature system
- `data/signatures.json` — data-driven; add/edit patterns here, no code changes needed
- Loaded by `signature_loader.py` → compiled to `Dict[str, Pattern]`
- 58 signatures across 30+ service categories
- False-positive filtering in `scanner_matcher.py`: placeholder detection, template vars (`${}`, `{{}}`, `<>`), low entropy, Firebase web config heuristics, localhost URIs, sequential/repetitive strings
- Supabase JWT role detection (anon vs service_role) in `scanner_matcher.py`

### AI client quirks
- Uses Groq's OpenAI-compatible API with `response_format: {"type": "json_object"}` for structured output
- `ask_json()` salvages JSON from model text wrappers (`_json_from_text()`) — finds first `{` to last `}`
- Retry: `max_retries` from config (default 1), 200ms sleep between retries
- No key validation before sending — invalid keys produce runtime `requests` errors

### Discovery quirks
- Default: 3-min lookback, 1-min chunks, 10 pages, 2s between pages
- Modes (from `--modes`): `new`, `trending`, `relevant`, `search_google`, `search_claude`, `search_openai`, `search_groq`, `search_hf`, `search_perplexity`, `search_replicate`, `search_openrouter`, `search_xai`, `search_cerebras`, `search_ai_all`
- Adaptive bisection: when `total_count >= 1000`, splits chunk in half recursively (max depth 10)
- Deduplicates against existing files (clean, failed, leaked) on write
- Proxy fallback: random shuffle, 250ms between proxy attempts, removes dead proxies from pool
- `search_*` modes use `/search/commits` endpoint; others use `/search/repositories`

### Package warnings suppressed
- `src/shared/requests_compat.py` calls `warnings.filterwarnings("ignore", ...)` for requests library compatibility — module-wide.

## Style conventions
- `from __future__ import annotations` in most files
- Rich Console for all user-facing output (no bare print except in APISniffer)
- Thread safety via `threading.Lock()` — io, ui, tag, proxy, good_proxy, manual_target locks
- JSON persistence: tempfile + fsync + atomic replace (`scanner_io.py`, `APISniffer.write_json_snapshot`)
- Scanner uses `ThreadPoolExecutor` with `FIRST_COMPLETED` wait strategy
