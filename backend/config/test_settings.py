import os
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-not-for-deployment")
from .settings import *  # noqa: F403
ALLOWED_HOSTS = ["testserver", "localhost"]
