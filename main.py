#!/usr/bin/env python3
"""X3r0Day API Sniffer — CLI entry point."""

import sys

if "--version" in sys.argv:
    from src import __version__
    print(f"X3r0Day API Sniffer v{__version__}")
    sys.exit(0)

from src.APIScanner import main as scanner_main
from src.AISearch import main as ai_search_main
from src.AIWorkflow import main as ai_workflow_main
from src.APIVerifier import main as verifier_main

COMMANDS = {
    "scan": scanner_main,
    "search": ai_search_main,
    "workflow": ai_workflow_main,
    "verify": verifier_main,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: python main.py <command>")
        print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
