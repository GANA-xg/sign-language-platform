import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Disable rate limiting during pytest runs
limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("TESTING") != "1",
)