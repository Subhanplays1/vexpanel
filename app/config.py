import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be configured; refusing insecure startup.")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(Path("instance") / "vexpanel.sqlite3"))
    VPS_PROVIDER = os.environ.get("VPS_PROVIDER", "custom_docker")
    DOCKER_NETWORK = os.environ.get("DOCKER_NETWORK", "vexpanel_network")
    BOOTSTRAP_ADMIN_EMAIL = os.environ.get("VEXPANEL_BOOTSTRAP_ADMIN_EMAIL")
    BOOTSTRAP_ADMIN_PASSWORD = os.environ.get("VEXPANEL_BOOTSTRAP_ADMIN_PASSWORD")
    PINGGY_AUTH_TOKEN = os.environ.get("PINGGY_AUTH_TOKEN")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true").lower() == "true"
