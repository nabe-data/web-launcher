import webbrowser

import pandas as pd

from streamlit_utils import _try_read_csv, open_urls, save_dataframe


def test_try_read_csv_utf8(tmp_path):
    p = tmp_path / "t_utf8.csv"
    p.write_text("NAME,URL\nA,https://example.com\n", encoding="utf-8")
    df = _try_read_csv(str(p))
    assert df is not None
    assert list(df.columns) == ["NAME", "URL"]
    assert df.iloc[0]["NAME"] == "A"


def test_try_read_csv_cp932(tmp_path):
    p = tmp_path / "t_cp932.csv"
    # write bytes with cp932 encoding
    p.write_bytes("NAME,URL\nB,https://example.org\n".encode("cp932"))
    df = _try_read_csv(str(p))
    assert df is not None
    assert df.iloc[0]["NAME"] == "B"


def test_save_dataframe_and_contents(tmp_path):
    out = tmp_path / "out.csv"
    df = pd.DataFrame({"NAME": ["X"], "URL": ["http://x"]})
    ok, msg = save_dataframe(df, str(out))
    assert ok is True
    assert out.exists()
    read = pd.read_csv(str(out))
    assert read.iloc[0]["NAME"] == "X"


def test_open_urls_calls_webbrowser(monkeypatch):
    called = []

    def fake_open(url):
        called.append(url)
        return True

    monkeypatch.setattr(webbrowser, "open", fake_open)

    urls = [None, "", "example.com", "https://ok.com", "mailto:me@example.com"]
    open_urls(urls)

    # scheme-less should have http:// prepended
    assert "http://example.com" in called
    assert "https://ok.com" in called
    assert "mailto:me@example.com" in called
    # ensure empty/None were not passed
    assert all(u is not None and u != "" for u in called)


def test_open_urls_handles_exceptions(monkeypatch):
    called = []

    def raise_for_first(url):
        if url and "bad" in url:
            raise RuntimeError("boom")
        called.append(url)
        return True

    monkeypatch.setattr(webbrowser, "open", raise_for_first)

    urls = ["bad.example", "good.example"]
    # should not raise
    open_urls(urls)
    # good.example should still be attempted (prefixed)
    assert any("good.example" in (u or "") for u in called)
