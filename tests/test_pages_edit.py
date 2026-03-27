import os
import sys
import importlib.util
from unittest.mock import MagicMock

import polars as pl

# プロジェクトルートを sys.path に追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Streamlit を事前にモックして、トップレベルの st.set_page_config 等を無害化する
mock_st = MagicMock()
mock_st.session_state = {}
sys.modules["streamlit"] = mock_st


# pages/02_編集.py をインポート
def import_edit_page():
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "pages", "02_編集.py")
    )
    spec = importlib.util.spec_from_file_location("edit_page", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


edit_page = import_edit_page()


def test_handle_create_mode_success(monkeypatch):
    mock_container = MagicMock()
    mock_container.text_input.return_value = "new.csv"
    mock_container.button.return_value = True

    # Mock save_dataframe
    monkeypatch.setattr(edit_page, "save_dataframe", lambda df, path: (True, "OK"))
    # Reset mock_st state
    edit_page.st.session_state = {}
    edit_page.st.rerun = MagicMock()

    # Mock os.path.exists
    monkeypatch.setattr(os.path, "exists", lambda p: False)

    edit_page.handle_create_mode("dummy_path", container=mock_container)

    assert edit_page.st.session_state["save_toast"] == "新しいCSVファイルを追加しました"
    assert edit_page.st.rerun.called


def test_handle_upload_mode_success(monkeypatch):
    mock_container = MagicMock()
    mock_file = MagicMock()
    mock_file.name = "upload.csv"
    mock_container.file_uploader.return_value = mock_file

    # Mock pl.read_csv
    monkeypatch.setattr(
        pl, "read_csv", lambda f: pl.DataFrame({"NAME": ["a"], "URL": ["b"]})
    )
    # Mock save_dataframe
    monkeypatch.setattr(edit_page, "save_dataframe", lambda df, path: (True, "OK"))
    # Mock st
    monkeypatch.setattr(edit_page.st, "session_state", {})
    monkeypatch.setattr(edit_page.st, "rerun", MagicMock())

    edit_page.handle_upload_mode("dummy_path", container=mock_container)

    assert (
        edit_page.st.session_state["save_toast"] == "CSVファイルをアップロードしました"
    )
    assert edit_page.st.rerun.called


def test_handle_edit_mode_save_success(monkeypatch):
    def fake_load(path):
        return ["test.csv"], [pl.DataFrame({"NAME": ["n"], "URL": ["u"]})]

    monkeypatch.setattr(edit_page, "load_csv_files", fake_load)
    monkeypatch.setattr(edit_page.st, "subheader", MagicMock())
    monkeypatch.setattr(edit_page.st, "data_editor", lambda df, **kwargs: df)
    # Mock button to return True for "保存する"
    monkeypatch.setattr(edit_page.st, "button", lambda *args, **kwargs: True)
    # Mock save_dataframe success
    monkeypatch.setattr(edit_page, "save_dataframe", lambda df, path: (True, "Saved"))
    monkeypatch.setattr(edit_page.st, "session_state", {})
    monkeypatch.setattr(edit_page.st, "rerun", MagicMock())

    edit_page.handle_edit_mode("dummy_path")
    assert edit_page.st.session_state["save_toast"] == "Saved"


def test_handle_create_mode_errors(monkeypatch):
    mock_container = MagicMock()

    # Empty name
    mock_container.text_input.return_value = ""
    mock_container.button.return_value = True
    edit_page.handle_create_mode("dummy_path", container=mock_container)
    assert mock_container.error.called

    # File exists
    mock_container.text_input.return_value = "exists.csv"
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    edit_page.handle_create_mode("dummy_path", container=mock_container)
    assert mock_container.error.called


def test_main(monkeypatch):
    monkeypatch.setattr(edit_page.st, "session_state", {"save_toast": "hello"})
    monkeypatch.setattr(edit_page.st, "toast", MagicMock())
    monkeypatch.setattr(edit_page.st, "subheader", MagicMock())
    monkeypatch.setattr(edit_page.st, "sidebar", MagicMock())

    # Mock handlers to avoid deep logic
    monkeypatch.setattr(edit_page, "handle_edit_mode", MagicMock())
    monkeypatch.setattr(edit_page, "handle_create_mode", MagicMock())
    monkeypatch.setattr(edit_page, "handle_upload_mode", MagicMock())

    edit_page.main()
    assert edit_page.st.toast.called
    assert "save_toast" not in edit_page.st.session_state
