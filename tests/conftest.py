"""
conftest.py
Shared pytest fixtures and path setup for the interactive-ai-agent test suite.
"""

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = REPO_ROOT / "app"
sys.path.insert(0, str(APP_DIR))


@pytest.fixture(scope="session")
def profile_path() -> str:
    return str(APP_DIR / "profile.yaml")


@pytest.fixture(scope="session")
def pdf_path() -> Path:
    return APP_DIR / "Gregory_E_Schwartz_Cv.pdf"


@pytest.fixture(scope="session")
def live_api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set — skipping live tests")
    return key
