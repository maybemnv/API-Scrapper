import argparse
import os

from . import scanner_state as state


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="X3r0Day API Leak Scanner")
    parser.add_argument("--threads", type=int, default=8, help="Number of worker threads")
    parser.add_argument("--max-download-mb", type=float, default=20.0, help="Max repo download size in MB")
    parser.add_argument("--line-cutoff", type=int, default=2000, help="Max line length scanned before splitting")
    parser.add_argument("--max-history-depth", type=int, default=5, help="Max commit-history patches to scan per repo")
    parser.add_argument("--no-commit-history", action="store_true", help="Disable commit-history scanning")
    parser.add_argument("--up-proxy", action="store_true", help="Use the upstream proxy list")
    parser.add_argument("--policy", type=str, default=None, help="Path to an AI policy file")
    return parser.parse_args(argv)


def apply_runtime_overrides(args):
    if args.threads and args.threads > 0:
        state.MAX_THREADS = args.threads
        state.available_thread_tags = deque(
            f"Thread-{i + 1}" for i in range(state.MAX_THREADS)
        )

    if args.max_download_mb and args.max_download_mb > 0:
        state.MAX_DOWNLOAD_SIZE_BYTES = int(args.max_download_mb * 1024 * 1024)

    if args.line_cutoff and args.line_cutoff > 0:
        state.LINE_CUTOFF = args.line_cutoff

    if args.max_history_depth is not None and args.max_history_depth >= 0:
        state.MAX_HISTORY_DEPTH = args.max_history_depth

    state.SCAN_COMMIT_HISTORY = not args.no_commit_history

    if args.up_proxy:
        os.environ["X3D_UP_PROXY"] = "1"


def reset_runtime_state(api_ref):
    from shared.api_signatures import build_api_signatures

    api_ref[0] = build_api_signatures(include_heroku=True)
