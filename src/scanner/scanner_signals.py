import signal

from . import scanner_state as state


def _handle_signal(signum, frame):
    request_shutdown()


def install_signal_handlers():
    try:
        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)
    except (ValueError, OSError, RuntimeError):
        pass


def request_shutdown():
    state.exit_prog = True
