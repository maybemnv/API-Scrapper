import json
import logging
import time
import urllib.parse
import urllib.request
from typing import Any, Dict

logger = logging.getLogger("api-sniffer.notifier")

_last_notification = 0.0
_MIN_INTERVAL = 5.0


def notify(webhook_url: str, finding: Dict[str, Any]) -> bool:
    global _last_notification
    parsed_url = urllib.parse.urlparse(webhook_url)
    if parsed_url.scheme not in {"http", "https"}:
        logger.warning("Webhook notification failed: unsupported URL scheme")
        return False

    now = time.time()
    if now - _last_notification < _MIN_INTERVAL:
        return False
    payload = json.dumps(
        {
            "text": f"New finding: {finding.get('type', 'Unknown')} in {finding.get('repo', 'unknown')}",
        }
    ).encode()
    try:
        req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)  # nosec B310
        _last_notification = now
        return True
    except Exception as e:
        logger.warning(f"Webhook notification failed: {e}")
        return False
