import warnings

warnings.filterwarnings("ignore", message=r".*doesn't match a supported version.*", category=UserWarning)

import requests as _requests  # noqa: E402

requests = _requests
