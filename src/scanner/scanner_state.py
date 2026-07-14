import threading
from collections import deque
from typing import Optional

PROXY_LIST_TXT: str = "live_proxies.txt"
UPDATE_PROXY_FILE: bool = False
MAX_THREADS: int = 5
MAX_HISTORY_DEPTH: int = 5
SCAN_HEROKU_KEYS: bool = False
SCAN_COMMIT_HISTORY: bool = True
PREFER_PROXY: bool = False
LOG_FILE: Optional[str] = None
DRY_RUN: bool = False
MAX_AGE_DAYS: int = 90
DEFAULT_BRANCH_FALLBACKS: list = ["main", "master"]
INCLUDE_EXTENSIONS: Optional[list] = None
EXCLUDE_EXTENSIONS: Optional[list] = None
QUEUE_JSON: str = "recent_repos.json"
AI_POL: Optional[dict] = None

pause_event: Optional[threading.Event] = None
exit_prog: bool = False
active_proxies: list = []
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

manual_target_mutex = threading.Lock()
io_mutex = threading.Lock()
ui_mutex = threading.Lock()
proxy_lock = threading.Lock()
good_proxy_lock = threading.Lock()
proxy_fail: dict = {}
good_proxies: set = set()
PROXY_FAIL_LIMIT: int = 5
