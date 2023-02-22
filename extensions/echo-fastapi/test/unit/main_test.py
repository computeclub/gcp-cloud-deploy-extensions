# -*- coding: utf-8 -*-
"""test the main source code."""

# import pytest
# from src.main import get_config_from_secret, get_pipeline_id, extension_is_enabled


def test_healthcheck(client):
    """test_healthcheck ensures the health endpoint check works."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
