import os

from rich.prompt import Prompt


def prompt_github_token():
    try:
        token = Prompt.ask(
            "[cyan]GitHub token (optional, press Enter to skip)[/]",
            default="",
            show_default=False,
            password=True,
        )
    except (EOFError, KeyboardInterrupt):
        return

    token = (token or "").strip()
    if token:
        os.environ["GITHUB_TOKEN"] = token
