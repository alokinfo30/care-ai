# tests/conftest.py
import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

@pytest.fixture
def client():
    app = create_app({'TESTING': True, 'DEBUG': False})
    with app.test_client() as client:
        yield client