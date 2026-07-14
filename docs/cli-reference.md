# CLI Reference

## main.py
| Flag | Description |
|------|-------------|
| `--up-proxy` | Persist healthy proxy pruning to `live_proxies.txt` |
| `--version` | Print version and exit |

## APISniffer.py (Discovery)
| Flag | Default | Description |
|------|---------|-------------|
| `--lookback-mins` | 3 | How far back to search |
| `--chunk-mins` | 1 | Time window per query chunk |
| `--pages-to-scrape` | 10 | Max GitHub result pages per chunk |
| `--proxy-retry-limit` | 200 | Max proxies to try before giving up |
| `--modes` | new,trending,relevant,... | Comma-separated search modes |

## APIScanner.py (Scanner)
| Flag | Default | Description |
|------|---------|-------------|
| `--max-threads` | 12 | Concurrent scanning workers |
| `--history-depth` | 10 | Recent commits to scan |
| `--scan-heroku-keys` | off | Enable Heroku key patterns |
| `--no-commit-history` | off | Disable commit history scanning |
| `--prefer-proxy` | off | Try proxy before direct IP |
| `--up-proxy` | off | Persist proxy pruning |

## AISearch.py (Query)
| Flag | Description |
|------|-------------|
| `--query TEXT` | Run one-shot query and exit |

## AIWorkflow.py
No CLI flags. Interactive NL interface.
