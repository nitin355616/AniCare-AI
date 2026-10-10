import sys
import os
from pathlib import Path

# Add backend directory and project root to sys.path so app and backend modules are importable
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pytest
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    """Session-scoped TestClient that manages the application lifespan."""
    with TestClient(app) as test_client:
        yield test_client
