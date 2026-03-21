import os
import sys

import streamlit

# tests/ から pytest を実行する際、プロジェクトルートをインポート可能にします
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_link_button


def test_create_link_button_with_url(monkeypatch):
    captured = {}

    def fake_link_button(name, url, width="stretch"):
        captured["name"] = name
        captured["url"] = url
        captured["use"] = width

    monkeypatch.setattr(streamlit, "link_button", fake_link_button)
    row = {"NAME": "N", "URL": "https://x"}
    create_link_button(row)
    assert captured["name"] == "N"
    assert captured["url"] == "https://x"
    assert captured["use"] == "stretch"


def test_create_link_button_no_url(monkeypatch):
    wrote = {}

    def fake_write(msg):
        wrote["msg"] = msg

    monkeypatch.setattr(streamlit, "write", fake_write)
    row = {"NAME": "N", "URL": ""}
    create_link_button(row)
    assert wrote["msg"] == "N"


def test_create_link_button_exception(monkeypatch):
    wrote = {}

    def fake_link_button(name, url, width="stretch"):
        raise RuntimeError("oops")

    def fake_write(msg):
        wrote["msg"] = msg

    monkeypatch.setattr(streamlit, "link_button", fake_link_button)
    monkeypatch.setattr(streamlit, "write", fake_write)
    row = {"NAME": "N", "URL": "https://x"}
    create_link_button(row)
    assert "行の表示中にエラーが発生しました" in wrote["msg"]
