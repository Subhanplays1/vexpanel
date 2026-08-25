import os
os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_PATH"] = "instance/test.sqlite3"
os.environ["VPS_PROVIDER"] = "mock"

from app import create_app

def test_health():
    client = create_app().test_client()
    assert client.get("/health").get_json()["success"] is True
