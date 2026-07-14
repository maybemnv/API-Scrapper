import threading
from collections import deque


MAX_THREADS = 8

MAX_DOWNLOAD_SIZE_BYTES = 20 * 1024 * 1024
LINE_CUTOFF = 2000
MAX_HISTORY_DEPTH = 5
SCAN_COMMIT_HISTORY = True

DEFAULT_BRANCH_FALLBACKS = ["main", "master"]

QUEUE_JSON = "recent_repos.json"
LEAKS_JSON = "leaked_keys.json"
DEAD_TARGETS_JSON = "failed_repos.json"
BORING_REPOS_JSON = "clean_repos.json"

AI_POL = None

exit_prog = False
is_typing_url = False
input_buffer = ""

ui_mutex = threading.Lock()
tag_mutex = threading.Lock()
pause_event = threading.Event()
pause_event.set()

scoreboard = {
    "total": 0,
    "remaining": 0,
    "scanned": 0,
    "clean": 0,
    "leaks": 0,
    "failed": 0,
}

thread_dashboard: dict = {}
log_history: list = []
leak_history: list = []
fail_history: list = []

available_thread_tags = deque(f"Thread-{i + 1}" for i in range(MAX_THREADS))
