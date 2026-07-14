import os
from typing import Optional


def _validate_github_token(token: str) -> bool:
    token = token.strip()
    valid_prefixes = ("github_pat_", "ghp_", "gho_", "ghu_", "ghs_", "ghr_")
    return any(token.startswith(p) and len(token) >= 30 for p in valid_prefixes)


def prompt_github_token(console=None) -> Optional[str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        if not _validate_github_token(token):
            print("[yellow][!] Warning: GITHUB_TOKEN format looks invalid. Expected github_pat_ or ghp_ prefix.[/]")
        return token
    return None
