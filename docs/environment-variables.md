# Environment Variables

## Required
| Variable | Used By | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | AIWorkflow, AISearch, Scanner live injection | Groq API key (starts with `gsk_`) |

## Optional
| Variable | Used By | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | APISniffer, APIScanner | GitHub PAT for higher rate limits |
| `GH_TOKEN` | APISniffer, APIScanner | Alias for GITHUB_TOKEN |
| `AI_POLICY_PATH` | AIWorkflow | Override path to `config/ai_policy.json` |
| `X3D_UP_PROXY` | Scanner | Set to `1` to persist proxy pruning |
