# Contributing

## Setup
```bash
uv sync --group dev
```

## Code Standards
- Follow existing style conventions
- Run Ruff before committing
- Add type hints to new functions
- Use Rich Console for user output

## Pull Request Workflow
1. Branch from `main`
2. Use descriptive commit messages
3. Add tests for new features
4. Update docs if changing CLI flags or env vars

## Testing
```bash
uv run pytest tests/ -v
```

## Security
Report vulnerabilities via GitHub Issues. See SECURITY.md.
