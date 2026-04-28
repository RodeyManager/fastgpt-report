"""Tests for POST /api/convert endpoint with multi-tool support."""
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_single_tool_default():
    """Default (no tools param) returns 1 result with markdownify."""
    resp = client.post("/api/convert", json={
        "raw_text": "<h1>Hello</h1>",
        "format_text": "",
        "file_ext": "html",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["tool"] == "markdownify"
    assert "Hello" in data["results"][0]["markdown"]
    assert data["results"][0]["duration_ms"] > 0


def test_explicit_single_markdownify():
    resp = client.post("/api/convert", json={
        "raw_text": "<h1>Hello</h1>",
        "format_text": "",
        "file_ext": "html",
        "tools": ["markdownify"],
    })
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1


def test_both_tools():
    resp = client.post("/api/convert", json={
        "raw_text": "<h1>Hello</h1><p>World</p>",
        "format_text": "",
        "file_ext": "html",
        "tools": ["markdownify", "markitdown"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["tool"] == "markdownify"
    assert data["results"][1]["tool"] == "markitdown"
    assert "Hello" in data["results"][0]["markdown"]
    assert "Hello" in data["results"][1]["markdown"]


def test_single_markitdown():
    resp = client.post("/api/convert", json={
        "raw_text": "<h1>Test</h1>",
        "format_text": "",
        "file_ext": "html",
        "tools": ["markitdown"],
    })
    assert resp.status_code == 200
    assert resp.json()["results"][0]["tool"] == "markitdown"


def test_invalid_tool_returns_422():
    resp = client.post("/api/convert", json={
        "raw_text": "x",
        "format_text": "",
        "file_ext": "html",
        "tools": ["nonexistent"],
    })
    assert resp.status_code == 422


def test_empty_tools_returns_422():
    resp = client.post("/api/convert", json={
        "raw_text": "x",
        "format_text": "",
        "file_ext": "html",
        "tools": [],
    })
    assert resp.status_code == 422


def test_result_has_all_fields():
    resp = client.post("/api/convert", json={
        "raw_text": "<h1>Hi</h1>",
        "format_text": "",
        "file_ext": "html",
        "tools": ["markdownify"],
    })
    result = resp.json()["results"][0]
    assert "tool" in result
    assert "markdown" in result
    assert "note" in result
    assert "duration_ms" in result
    assert isinstance(result["duration_ms"], (int, float))
