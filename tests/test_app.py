import os
import sys

import pandas as pd
import streamlit

# ensure project root is importable when running pytest from tests/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_link_button


def test_create_link_button_with_url(monkeypatch):
    captured = {}

    def fake_link_button(name, url, use_container_width=True):
        captured["name"] = name
        captured["url"] = url
        captured["use"] = use_container_width

    monkeypatch.setattr(streamlit, "link_button", fake_link_button)
    row = pd.Series({"NAME": "N", "URL": "https://x"})
    create_link_button(row)
    assert captured["name"] == "N"
    assert captured["url"] == "https://x"
    assert captured["use"] is True


def test_create_link_button_no_url(monkeypatch):
    wrote = {}

    def fake_write(msg):
        wrote["msg"] = msg

    monkeypatch.setattr(streamlit, "write", fake_write)
    row = pd.Series({"NAME": "N", "URL": ""})
    create_link_button(row)
    assert wrote["msg"] == "N"


def test_create_link_button_exception(monkeypatch):
    wrote = {}

    def fake_link_button(name, url, use_container_width=True):
        raise RuntimeError("oops")

    def fake_write(msg):
        wrote["msg"] = msg

    monkeypatch.setattr(streamlit, "link_button", fake_link_button)
    monkeypatch.setattr(streamlit, "write", fake_write)
    row = pd.Series({"NAME": "N", "URL": "https://x"})
    create_link_button(row)
    assert "行の表示中にエラーが発生しました" in wrote["msg"]
