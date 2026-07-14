import json
import logging
import sys
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        })


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO):
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,
    )
    for handler in handlers:
        handler.setFormatter(JSONFormatter())
    return logging.getLogger("api-sniffer")
