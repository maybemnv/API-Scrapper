# Architecture

```
┌──────────────┐
│   main.py    │  TUI Launcher / Control Center
│              │  Enter = AI Workflow
│              │  Manual = Numbered Menu
└──────┬───────┘
       │
       ├──────────────────────────────────┐
       ▼                                  ▼
┌──────────────┐              ┌──────────────────┐
│ AIWorkflow   │              │  Manual Control  │
│ (NL → plan)  │              │  Center (Menu)   │
└──────┬───────┘              └────────┬─────────┘
       │                               │
       ▼                               ▼
┌─────────────────────────────────────────────────┐
│              Subprocess Launcher                │
│  uv run python src/APISniffer.py [flags]        │
│  uv run python src/APIScanner.py [flags]        │
│  uv run python src/AISearch.py [--query "..."]  │
└─────────────────────────────────────────────────┘
```

## Data Flow

1. **Discovery** (`APISniffer.py`): Queries GitHub Search API for recently created public repos. Deduplicates against existing results. Writes to `recent_repos.json`.

2. **Scanning** (`APIScanner.py` + `src/scanner/`): Reads `recent_repos.json`. Downloads each repo as a ZIP/tarball (or git clone). Scans file contents against compiled regex signatures from `data/signatures.json`. Writes findings to `leaked_keys.json`, clean repos to `clean_repos.json`, and failures to `failed_repos.json`.

3. **AI Search** (`AISearch.py` + `src/shared/ai_search_runtime.py`): Reads `leaked_keys.json`. Uses Groq LLM to interpret natural language queries and filter/display results.

## Shared Modules

- `src/shared/ai_client.py` — Groq API calls
- `src/shared/scanner_matcher.py` — Regex matching, false-positive filtering, private key detection
- `src/shared/signature_loader.py` — Compiles `data/signatures.json` into `Dict[str, Pattern]`
- `src/shared/category_routing.py` — Maps NL queries to signature categories
