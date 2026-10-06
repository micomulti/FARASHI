"""Test setup: lets pytest find the app package, and keeps tests away from your real database."""
import os
import tempfile

_db = os.path.join(tempfile.mkdtemp(), "test.db").replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{_db}"
os.environ["MOCK_MODE"] = "true"
