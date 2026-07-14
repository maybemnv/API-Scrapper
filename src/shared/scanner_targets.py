import re
from typing import List, Optional

from shared.ai_client import ask_json, build_msgs, get_key, remember_exchange
from shared.ai_policy import fill_tpl, load_pol

GITHUB_REPO_PATTERN = re.compile(
    r"(?:https?://github\.com/)?([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+?)(?:\.git)?(?:/|\s|$)"
)


def _sanitize_input(text: str) -> str:
    sanitized = re.sub(r"[;&|`$(){}[\]<>#!\"']", "", text)
    return sanitized


def resolve_repo_targets(user_text: str, api_key: Optional[str] = None, console=None) -> List[str]:
    text = _sanitize_input(user_text)
    url_matches = GITHUB_REPO_PATTERN.findall(text)
    repos = []
    seen = set()

    for match in url_matches:
        repo = match.strip().strip("/")
        if repo and repo not in seen:
            seen.add(repo)
            repos.append(repo)

    if not repos and api_key:
        pol = load_pol()
        if pol:
            sys_tpl = pol.get("repo_targets", {}).get("system", "")
            if sys_tpl:
                ctx = {"__POLICY__": ""}
                msgs = build_msgs(fill_tpl(sys_tpl, ctx), text)
                cfg = pol.get("llm", {})
                try:
                    result = ask_json(msgs, api_key, cfg)
                    ai_repos = result.get("targets", [])
                    for r in ai_repos:
                        if isinstance(r, str) and r not in seen:
                            seen.add(r)
                            repos.append(r)
                except Exception:
                    pass

    return repos
