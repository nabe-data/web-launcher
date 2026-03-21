import os
import sys

# tests/ から pytest を実行する際、プロジェクトルートをインポート可能にします
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app
from app import create_link_button


def test_create_link_button_with_url(monkeypatch):
    captured = {}

    def fake_link_button(name, url, width="stretch"):
        captured["name"] = name
        captured["url"] = url
        captured["use"] = width

    monkeypatch.setattr(app.st, "link_button", fake_link_button)
    row = {"NAME": "N", "URL": "https://x"}
    create_link_button(row)
    assert captured["name"] == "N"
    assert captured["url"] == "https://x"
    assert captured["use"] == "stretch"


def test_create_link_button_no_url(monkeypatch):
    wrote = {}

    def fake_write(msg):
        wrote["msg"] = msg

    monkeypatch.setattr(app.st, "write", fake_write)
    row = {"NAME": "N", "URL": ""}
    create_link_button(row)
    assert wrote["msg"] == "N"


def test_create_link_button_no_name(monkeypatch):
    wrote = {}

    def fake_write(msg):
        wrote["msg"] = msg

    monkeypatch.setattr(app.st, "write", fake_write)
    row = {"URL": ""}  # NAME is missing
    create_link_button(row)
    assert wrote["msg"] == "Unknown"


def test_create_link_button_exception(monkeypatch):
    wrote = {}

    def fake_link_button(name, url, width="stretch"):
        raise RuntimeError("oops")

    def fake_write(msg):
        wrote["msg"] = msg

    monkeypatch.setattr(app.st, "link_button", fake_link_button)
    monkeypatch.setattr(app.st, "write", fake_write)
    row = {"NAME": "N", "URL": "https://x"}
    create_link_button(row)
    assert "行の表示中にエラーが発生しました" in wrote["msg"]


def test_main_no_files(monkeypatch):
    import app

    # Mock load_csv_files to return empty lists
    def fake_load(path):
        return [], []

    monkeypatch.setattr(app, "load_csv_files", fake_load)
    monkeypatch.setattr(app.st, "set_page_config", lambda **kwargs: None)
    monkeypatch.setattr(app.st, "warning", lambda msg: None)

    # We just want to see if it runs without error when no files are found
    app.main()


def test_main_with_files(monkeypatch):
    import polars as pl

    import app

    def fake_load(path):
        return ["test.csv"], [pl.DataFrame({"NAME": ["n"], "URL": ["http://u"]})]

    monkeypatch.setattr(app, "load_csv_files", fake_load)
    monkeypatch.setattr(
        app.st,
        "sidebar",
        type("Mock", (), {"radio": lambda *args, **kwargs: "test.csv"}),
    )
    monkeypatch.setattr(app.st, "header", lambda msg: None)
    monkeypatch.setattr(app.st, "button", lambda *args, **kwargs: False)
    # mock create_link_button to avoid deeper streamlit calls
    monkeypatch.setattr(app, "create_link_button", lambda row: None)

    app.main()
