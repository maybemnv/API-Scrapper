# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
# ---------------------------------------------------------------------------------- #


import threading
from collections import deque
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Set

MAX_THREADS = 12
SCAN_HEROKU_KEYS = False
SCAN_COMMIT_HISTORY = True
MAX_HISTORY_DEPTH = 10

FAT_FILE_LIMIT = 50 * 1024 * 1024
LINE_CUTOFF = 2000
MAX_DOWNLOAD_SIZE_BYTES = 100 * 1024 * 1024

NET_TIMEOUTS = (5.0, 15.0)
IDLE_STALL_TIMEOUT_SEC = 25.0
PROXY_TIMEOUTS = (15.0, 20.0)
PREFER_PROXY = False
UPDATE_PROXY_FILE = False

PROXY_FAIL_LIMIT = 1

ROOT_DIR = Path(__file__).resolve().parents[2]
QUEUE_JSON = str(ROOT_DIR / "recent_repos.json")
LEAKS_JSON = str(ROOT_DIR / "leaked_keys.json")
DEAD_TARGETS_JSON = str(ROOT_DIR / "failed_repos.json")
BORING_REPOS_JSON = str(ROOT_DIR / "clean_repos.json")
PROXY_LIST_TXT = str(ROOT_DIR / "live_proxies.txt")

DEFAULT_BRANCH_FALLBACKS = ("main", "master")
SPOOFED_USER_AGENT = "Wget/1.21.2"

TARGET_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".yml",
    ".yaml",
    ".xml",
    ".txt",
    ".env",
    ".ini",
    ".conf",
    ".config",
    ".sh",
    ".bash",
    ".php",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".rs",
    ".sql",
    ".md",
    ".toml",
    ".properties",
    "tfvars",
    ".tf",
    ".hcl",
    ".gradle",
    ".plist",
    ".cfg",
    ".envrc",
    ".lua",
    ".dart",
    ".zsh",
    ".fish",
    ".bat",
    ".cmd",
    ".psm1",
    "ps1",
)
EXACT_FILENAMES = ("dockerfile", "makefile", "gemfile")

pause_event: Optional[threading.Event] = None
exit_prog: bool = False
active_proxies: List[str] = []
good_proxies: Set[str] = set()

is_typing_url: bool = False
input_buffer: str = ""
manual_target_queue: Deque[Dict[str, Any]] = deque()
manual_target_names: Set[str] = set()

available_thread_tags: Deque[str] = deque()
thread_dashboard: Dict[str, Dict[str, Any]] = {}

log_history: Deque[str] = deque(maxlen=6)
fail_history: Deque[str] = deque(maxlen=10)
leak_history: Deque[str] = deque(maxlen=10)
scoreboard: Dict[str, int] = {"total": 0, "scanned": 0, "leaks": 0, "clean": 0, "failed": 0, "remaining": 0}

ui_mutex = threading.Lock()
io_mutex = threading.Lock()
tag_mutex = threading.Lock()
proxy_lock = threading.Lock()
good_proxy_lock = threading.Lock()
manual_target_mutex = threading.Lock()

proxy_fail: Dict[str, int] = {}

AI_POL: Dict[str, Any] = {}
