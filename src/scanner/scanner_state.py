# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
# ---------------------------------------------------------------------------------- #

import threading
from collections import deque
from typing import Optional

MAX_THREADS: int = 5
MAX_HISTORY_DEPTH: int = 500
SCAN_HEROKU_KEYS: bool = False
SCAN_COMMIT_HISTORY: bool = True
PREFER_PROXY: bool = False
UPDATE_PROXY_FILE: bool = False

PROXY_LIST_TXT: str = "live_proxies.txt"
DEFAULT_BRANCH_FALLBACKS: list = ["master", "main"]
PROXY_FAIL_LIMIT: int = 3

proxy_lock = threading.Lock()
good_proxy_lock = threading.Lock()
ui_mutex = threading.Lock()
io_mutex = threading.Lock()
manual_target_mutex = threading.Lock()

active_proxies: list = []
good_proxies: set = set()
proxy_fail: dict = {}

pause_event: Optional[threading.Event] = None
exit_prog: bool = False

is_typing_url: bool = False
input_buffer: str = ""
manual_target_queue: deque = deque()
manual_target_names: set = set()

available_thread_tags: deque = deque()
thread_dashboard: dict = {}
log_history: deque = deque(maxlen=6)
fail_history: deque = deque(maxlen=10)
leak_history: deque = deque(maxlen=10)
scoreboard: dict = {"total": 0, "scanned": 0, "leaks": 0, "clean": 0, "failed": 0, "remaining": 0}

QUEUE_JSON: str = "data/queue.json"
AI_POL: Optional[dict] = None

LOG_FILE: Optional[str] = None
DRY_RUN: bool = False
MAX_AGE_DAYS: Optional[int] = None
