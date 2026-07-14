#!/usr/bin/env python3
# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
#              You are free to use, modify, and redistribute this code,              #
#          provided proper credit is given to the original project X3r0Day.          #
# ---------------------------------------------------------------------------------- #

import argparse
import json
import os
import random
import signal
import sys
import tempfile
import time
import threading
from pathlib import Path
from typing import List, Optional
from itertools import cycle

from shared.requests_compat import requests
from datetime import datetime, timedelta, timezone


LOOKBACK_MINS = 3
CHUNK_MINS = 1

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_QUEUE_FILE = str(ROOT_DIR / "recent_repos.json")
PROXY_FILE = str(ROOT_DIR / "live_proxies.txt")

RESULTS_PER_PAGE = 100
PAGES_TO_SCRAPE = 10
NET_TIMEOUT = 10
PROXY_RETRY_LIMIT = 200
MAX_SPLIT_DEPTH = 10

SCANNED_HISTORY = [
    str(ROOT_DIR / "clean_repos.json"),
    str(ROOT_DIR / "failed_repos.json"),
    str(ROOT_DIR / "leaked_keys.json"),
]

SPOOFED_UA = "XeroDay-APISniffer/1.0"
shutdown_requested = False
MODES = ["new", "trending", "relevant", "search_google", "search_claude", "search_openai", "search_groq", "search_hf", "search_perplexity", "search_replicate", "search_openrouter", "search_xai", "search_cerebras", "search_ai_all"]


class RateLimiter:
    def __init__(self, rate: float = 1.0):
        self.rate = rate
        self.tokens = rate
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                self._last = now + sleep_time
                time.sleep(sleep_time)
                self.tokens = 0
            else:
                self.tokens -= 1
                self._last = now


class DiscoveryRequestError(RuntimeError):
    pass


def parse_args():
    parser = argparse.ArgumentParser(description="Discover recent GitHub repositories.")
    parser.add_argument("--lookback-mins", type=int, help="How far back to search for repositories.")
    parser.add_argument("--chunk-mins", type=int, help="Time window per query chunk.")
    parser.add_argument("--pages-to-scrape", type=int, help="Maximum GitHub result pages to fetch per chunk.")
    parser.add_argument("--proxy-retry-limit", type=int, help="Maximum proxies to try before giving up.")
    parser.add_argument("--modes", type=str, help="Comma-separated scan modes.")
    return parser.parse_args()


def apply_runtime_overrides(args):
    global LOOKBACK_MINS, CHUNK_MINS, PAGES_TO_SCRAPE, PROXY_RETRY_LIMIT, MODES
    if args.lookback_mins is not None:
        LOOKBACK_MINS = max(1, args.lookback_mins)
    if args.chunk_mins is not None:
        CHUNK_MINS = max(1, args.chunk_mins)
    if args.pages_to_scrape is not None:
        PAGES_TO_SCRAPE = max(1, args.pages_to_scrape)
    if args.proxy_retry_limit is not None:
        PROXY_RETRY_LIMIT = max(1, args.proxy_retry_limit)
    if args.modes is not None:
        valid_modes = {"new", "trending", "relevant", "search_google", "search_claude", "search_openai", "search_groq", "search_hf", "search_perplexity", "search_replicate", "search_openrouter", "search_xai", "search_cerebras", "search_ai_all"}
        parsed_modes = [m.strip().lower() for m in args.modes.split(",")]
        MODES = [m for m in parsed_modes if m in valid_modes]
        if not MODES:
            MODES = ["new", "trending", "relevant", "search_google", "search_claude"]


def get_tokens() -> List[str]:
    tokens = []
    for var in ("GITHUB_TOKEN", "GH_TOKEN"):
        val = os.environ.get(var, "").strip()
        if val:
            tokens.append(val)
    bulk = os.environ.get("GITHUB_TOKENS", "").strip()
    if bulk:
        for t in bulk.split(","):
            t = t.strip()
            if t:
                tokens.append(t)
    seen = set()
    deduped = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def mask_token(token: str) -> str:
    if len(token) <= 8:
        return token[:4] + "****"
    return token[:4] + "****" + token[-4:]


def grab_proxies(filepath: str = PROXY_FILE) -> List[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def get_search_query(start_time: datetime, end_time: datetime, page: int = 1, query_type: str = "new"):
    start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    if query_type == "trending":
        return {"q": f"pushed:{start_str}..{end_str} stars:>50", "sort": "stars", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "relevant":
        return {"q": f"API OR LLM OR key OR secret OR security pushed:{start_str}..{end_str}", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_google":
        return {"q": f"AIzaSy author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_claude":
        return {"q": f"sk-ant-api author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_openai":
        return {"q": f"sk-proj author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_groq":
        return {"q": f"gsk_ author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_hf":
        return {"q": f"hf_ author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_perplexity":
        return {"q": f"pplx- author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_replicate":
        return {"q": f"r8_ author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_openrouter":
        return {"q": f"sk-or-v1- author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_xai":
        return {"q": f"xai- author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}
    elif query_type == "search_cerebras":
        return {"q": f"cs- author-date:{start_str}..{end_str}", "sort": "author-date", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}

    return {"q": f"created:{start_str}..{end_str}", "sort": "created", "order": "desc", "per_page": RESULTS_PER_PAGE, "page": page}


def format_proxy_dict(ip_port: str) -> dict:
    return {"http": f"http://{ip_port}", "https": f"http://{ip_port}"}


def remove_proxy(proxy_pool: List[str], proxy_ip: str) -> None:
    try:
        proxy_pool.remove(proxy_ip)
    except ValueError:
        pass


def request_shutdown(_signum, _frame):
    global shutdown_requested
    if shutdown_requested:
        raise KeyboardInterrupt
    shutdown_requested = True
    print("\n[!] Ctrl+C received. Stopping after the current request.", flush=True)


def install_signal_handlers():
    signal.signal(signal.SIGINT, request_shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_shutdown)


def interruptible_sleep(seconds: float) -> bool:
    deadline = time.time() + max(0.0, seconds)
    while time.time() < deadline:
        if shutdown_requested:
            return False
        time.sleep(min(0.1, deadline - time.time()))
    return not shutdown_requested


def write_json_snapshot(payload: list, filename: str):
    directory = os.path.dirname(os.path.abspath(filename)) or "."
    file_prefix = f".{os.path.basename(filename)}."
    fd, temp_path = tempfile.mkstemp(prefix=file_prefix, suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, indent=4)
            fp.flush()
            os.fsync(fp.fileno())
        os.replace(temp_path, filename)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def ensure_json_list_file(filename: str):
    if not os.path.exists(filename):
        write_json_snapshot([], filename)


def build_github_headers(token_value: Optional[str] = None) -> dict:
    headers = {"User-Agent": SPOOFED_UA}
    if token_value:
        normalized = token_value.strip()
        lowered = normalized.lower()
        if lowered.startswith("bearer ") or lowered.startswith("token "):
            headers["Authorization"] = normalized
        else:
            headers["Authorization"] = f"Bearer {normalized}"
    return headers


def make_request(session_obj, endpoint: str, query: dict, ips: List[str], rate_limiter: Optional[RateLimiter] = None, token_value: Optional[str] = None):
    if shutdown_requested:
        raise KeyboardInterrupt

    if rate_limiter:
        rate_limiter.acquire()

    headers = build_github_headers(token_value)
    if token_value:
        print(f"  [i] Using token: {mask_token(token_value)}")

    direct_error = None
    try:
        req = session_obj.get(endpoint, params=query, headers=headers, timeout=NET_TIMEOUT)
    except requests.RequestException as exc:
        direct_error = exc
        req = None

    if req is not None and req.status_code == 200:
        return req

    if not ips:
        if req is None:
            raise DiscoveryRequestError("Direct connection failed and no proxies loaded.") from direct_error
        return req

    pool = ips[:]
    random.shuffle(pool)
    tried = 0
    last_error = direct_error
    for ip in pool:
        if tried >= PROXY_RETRY_LIMIT:
            break
        tried += 1
        proxies = format_proxy_dict(ip)
        try:
            r = session_obj.get(endpoint, params=query, headers=headers, proxies=proxies, timeout=NET_TIMEOUT)
            if r.status_code == 200:
                print(f"[+] Success using proxy: {ip}")
                return r
            print(f"[-] Proxy {ip} hit status {r.status_code}. Skipping...")
            if not interruptible_sleep(0.25):
                raise KeyboardInterrupt
        except requests.RequestException as e:
            last_error = e
            remove_proxy(ips, ip)
            print(f"[-] Proxy {ip} failed. Removing from pool.")
            if not interruptible_sleep(0.15):
                raise KeyboardInterrupt

    if req is not None:
        return req
    if last_error is not None:
        raise DiscoveryRequestError(f"Direct request failed and no working proxies remained. Last error: {last_error}") from last_error
    raise DiscoveryRequestError("Exhausted all options.")


def sync_results_to_disk(raw_json: dict, filename: str = TARGET_QUEUE_FILE):
    incoming_data = raw_json.get("items", [])
    if not incoming_data:
        return 0
    blacklist = set()
    current_queue = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                current_queue = json.load(f)
                for item in current_queue:
                    blacklist.add(item.get("name"))
        except json.JSONDecodeError:
            pass
    for log_file in SCANNED_HISTORY:
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for entry in json.load(f):
                        repo_id = entry.get("repo") or entry.get("name")
                        if repo_id:
                            blacklist.add(repo_id)
            except json.JSONDecodeError:
                pass
    new_finds = 0
    for entry in incoming_data:
        target_repo = entry.get("repository", entry)
        full_path = target_repo.get("full_name")
        if not full_path:
            continue
        if full_path not in blacklist:
            created_at = target_repo.get("created_at") or entry.get("commit", {}).get("author", {}).get("date")
            current_queue.append({"name": full_path, "created_at": created_at, "url": target_repo.get("html_url"), "stars": target_repo.get("stargazers_count", 0)})
            blacklist.add(full_path)
            new_finds += 1
    current_queue.sort(key=lambda x: x["created_at"], reverse=True)
    write_json_snapshot(current_queue, filename)
    return new_finds


def main():
    global shutdown_requested
    shutdown_requested = False
    ensure_json_list_file(TARGET_QUEUE_FILE)

    api_url = "https://api.github.com/search/repositories"
    proxies = grab_proxies()
    tokens = get_tokens()
    token_cycle = cycle(tokens) if tokens else None
    rate_limiter = RateLimiter(rate=2.0)

    print(f"[*] Scouring GitHub for repos from the last {LOOKBACK_MINS} minutes (using {CHUNK_MINS}-min chunks with adaptive bisection)...")
    if proxies:
        print(f"[*] Loaded {len(proxies)} proxies as fallback.")
    else:
        print("[*] No proxies loaded. Using direct connection only.")
    if tokens:
        print(f"[*] Loaded {len(tokens)} GitHub tokens for rotation.")

    http_session = requests.Session()
    total_new_finds = 0
    interrupted = False

    try:
        now = datetime.now(timezone.utc)
        newest = now - timedelta(minutes=LOOKBACK_MINS)
        chunks = []
        cursor = newest
        while cursor < now:
            chunk_end = min(cursor + timedelta(minutes=CHUNK_MINS), now)
            if "new" in MODES:
                chunks.append((cursor, chunk_end, "new"))
            if "trending" in MODES:
                chunks.append((cursor, chunk_end, "trending"))
            if "relevant" in MODES:
                chunks.append((cursor, chunk_end, "relevant"))
            ai_types = ["search_google", "search_claude", "search_openai", "search_groq", "search_hf", "search_perplexity", "search_replicate", "search_openrouter", "search_xai", "search_cerebras"]
            if "search_ai_all" in MODES:
                for ai_mode in ai_types:
                    chunks.append((cursor, chunk_end, ai_mode))
            else:
                for ai_mode in ai_types:
                    if ai_mode in MODES:
                        chunks.append((cursor, chunk_end, ai_mode))
            cursor = chunk_end

        chunks.reverse()
        print(f"[*] Planning to scan {len(chunks)} chunks")
        print(f"[*] Time range: {newest.strftime('%H:%M:%S')} → {now.strftime('%H:%M:%S')} UTC\n")

        chunk_idx = 0
        while chunks:
            if shutdown_requested:
                interrupted = True
                break
            chunk_item = chunks.pop(0)
            if len(chunk_item) == 2:
                start_time, end_time = chunk_item
                query_type = "new"
            else:
                start_time, end_time, query_type = chunk_item
            chunk_idx += 1

            current_token = next(token_cycle) if token_cycle else None

            if query_type.startswith("search_"):
                current_api_url = "https://api.github.com/search/commits"
            else:
                current_api_url = "https://api.github.com/search/repositories"

            t_start = start_time.strftime('%H:%M:%S')
            t_end = end_time.strftime('%H:%M:%S')
            print(f"{'='*60}")
            print(f"[Chunk {chunk_idx}] {t_start} -> {t_end} UTC | Type: {query_type}")

            api_query = get_search_query(start_time, end_time, page=1, query_type=query_type)
            try:
                req = make_request(http_session, current_api_url, api_query, proxies, rate_limiter, current_token)
            except DiscoveryRequestError as exc:
                print(f"  [-] Chunk request failed. {exc}")
                continue

            if req.status_code == 422:
                print("  [-] Target chunk rejected (422).")
                continue
            elif req.status_code != 200:
                print(f"  [-] Request failed with status {req.status_code}")
                continue

            raw_json = req.json()
            repo_count = raw_json.get("total_count", 0)
            found_repos = raw_json.get("items", [])
            if not found_repos:
                print("  [-] No repos in this chunk.")
                continue
            print(f"  [i] Sniffer shows {repo_count} repos here")

            if repo_count >= 1000:
                mid_point = start_time + (end_time - start_time) / 2
                if (mid_point - start_time).total_seconds() < 1:
                    print("  [!] Chunk too small to split.")
                elif query_type.startswith("search_"):
                    print(f"  [!] Search reached {repo_count} hits. Grabbing what we fetched...")
                else:
                    print(f"  [↓] Hit 1k cap. Splitting chunk...")
                    chunks.insert(0, (start_time, mid_point, query_type))
                    chunks.insert(0, (mid_point, end_time, query_type))
                    chunk_idx -= 1
                    continue

            pages_needed = min((repo_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE, PAGES_TO_SCRAPE)
            saved = sync_results_to_disk(raw_json)
            total_new_finds += saved
            print(f"  -> Page 1/{pages_needed}: +{saved} fresh targets")

            for page_num in range(2, pages_needed + 1):
                if shutdown_requested:
                    interrupted = True
                    break
                if not interruptible_sleep(2):
                    interrupted = True
                    break

                current_token = next(token_cycle) if token_cycle else None
                api_query = get_search_query(start_time, end_time, page=page_num, query_type=query_type)
                print(f"  -> Fetching Page {page_num}/{pages_needed}...")
                try:
                    req = make_request(http_session, current_api_url, api_query, proxies, rate_limiter, current_token)
                except DiscoveryRequestError as exc:
                    print(f"  [-] Page {page_num} failed. {exc}")
                    break
                if req.status_code == 422:
                    print("  [-] Max pagination.")
                    break
                elif req.status_code != 200:
                    print(f"  [-] Page {page_num} status {req.status_code}.")
                    break
                page_json = req.json()
                if not page_json.get("items"):
                    break
                loot = sync_results_to_disk(page_json)
                total_new_finds += loot
                print(f"     +{loot} fresh targets")

    except KeyboardInterrupt:
        interrupted = True
        print("\n[!] Discovery interrupted.", flush=True)
    finally:
        http_session.close()

    print(f"\n{'='*60}")
    if interrupted or shutdown_requested:
        print(f"[!] Stopped early. Saved {total_new_finds} new targets.")
    else:
        print(f"[+] Done! Added {total_new_finds} total new targets.")


if __name__ == "__main__":
    install_signal_handlers()
    apply_runtime_overrides(parse_args())
    main()
