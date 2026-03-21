import os
import sys

import polars as pl

# tests/ から pytest を実行する際、sys.path にプロジェクトルートを追加します
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streamlit_utils import _try_read_csv, load_csv_files, open_urls, save_dataframe


def test_try_read_csv_utf8(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text("col1,col2\n1,2\n", encoding="utf-8")
    df = _try_read_csv(str(p))
    assert df is not None
    assert list(df.columns) == ["col1", "col2"]


def test_try_read_csv_shiftjis(tmp_path, monkeypatch):
    p = tmp_path / "sjis.csv"
    p.write_bytes("名前,URL\nあい,https://example.com\n".encode("shift_jis"))
    # tests/ から pytest を実行する際、プロジェクトルートをインポート可能にします
    monkeypatch.syspath_prepend(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )
    df = _try_read_csv(str(p))
    assert df is not None
    assert "名前" in df.columns


def test_load_csv_files_nonexistent(tmp_path):
    dirp = tmp_path / "noexist"
    csvs, dfs = load_csv_files(str(dirp))
    assert csvs == []
    assert dfs == []


def test_load_csv_files_with_files(tmp_path):
    dirp = tmp_path
    f1 = dirp / "1.csv"
    f1.write_text("A,B\n1,2\n", encoding="utf-8")
    f2 = dirp / "bad.csv"
    f2.write_bytes(b"\xff\xff")
    csvs, dfs = load_csv_files(str(dirp))
    assert len(csvs) == 2
    assert len(dfs) == 2
    names = [os.path.basename(p) for p in csvs]
    assert "1.csv" in names and "bad.csv" in names
    idx1 = names.index("1.csv")
    idx2 = names.index("bad.csv")
    assert dfs[idx1].height == 1
    assert dfs[idx2].is_empty()


def test_save_dataframe(tmp_path):
    df = pl.DataFrame({"a": [1, 2]})
    out = tmp_path / "sub" / "out.csv"
    ok, msg = save_dataframe(df, str(out))
    assert ok is True
    assert isinstance(msg, str) and msg
    assert out.exists()
    df2 = pl.read_csv(out)
    assert list(df2.columns) == ["a"]
    assert df2.height == 2


def test_save_dataframe_fail(tmp_path, monkeypatch):
    import polars as pl

    df = pl.DataFrame({"a": [1]})
    out = tmp_path / "out.csv"

    def fake_write_csv(self, path):
        raise RuntimeError("write fail")

    monkeypatch.setattr(pl.DataFrame, "write_csv", fake_write_csv)
    ok, msg = save_dataframe(df, str(out))
    assert ok is False
    assert "保存に失敗しました" in msg


def test_save_dataframe_cleanup_fail(tmp_path, monkeypatch):
    import polars as pl

    df = pl.DataFrame({"a": [1]})
    out = tmp_path / "out.csv"

    # os.remove が失敗するケース（finally ブロックのテスト）
    def fake_remove(path):
        raise RuntimeError("remove fail")

    monkeypatch.setattr(os, "remove", fake_remove)
    # 正常系でも os.remove は呼ばれる（tmp_path は os.replace で消えるはずだが、コード上は finally でチェックしている）
    # 実際には os.replace が成功すると tmp_path は無くなるので os.path.exists(tmp_path) は False になる。
    # なので、失敗させて tmp_path が残る状態にする必要がある。

    def fake_replace(src, dst):
        raise RuntimeError("replace fail")

    monkeypatch.setattr(os, "replace", fake_replace)

    ok, msg = save_dataframe(df, str(out))
    assert ok is False
    # finally ブロックで os.remove が呼ばれ、例外が発生するが、pass されるはず。
    # これを確認するのは難しいが、カバレッジは通るはず。


def test_open_urls(monkeypatch):
    called = []

    def fake_open(url):
        if "bad" in url:
            raise Exception("boom")
        called.append(url)
        return True

    monkeypatch.setattr("webbrowser.open", fake_open)
    urls = ["https://ok", "bad://url", "", None]
    failed = open_urls(urls)
    assert "bad://url" in failed
    assert "https://ok" in called
