# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
# ---------------------------------------------------------------------------------- #

import argparse
import logging
import sys

from src.logging_setup import setup_logging
from src.scanner import scanner_state as state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="X3r0Day API Sniffer")
    parser.add_argument("--log-file", type=str, help="Path to write JSON log file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing results")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.log_file:
        state.LOG_FILE = args.log_file
        setup_logging(log_file=args.log_file)
    else:
        setup_logging()

    if args.dry_run:
        state.DRY_RUN = True
        logging.getLogger("api-sniffer").info("Dry-run mode enabled — no results will be written")


if __name__ == "__main__":
    main()
