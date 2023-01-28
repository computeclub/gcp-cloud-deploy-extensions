# -*- coding: utf-8 -*-
"""Test factories."""
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    """client is a fixture containing a test app."""
    with TestClient(app) as test_client:
        yield test_client
