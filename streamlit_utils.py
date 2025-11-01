import glob
import os
import tempfile
import webbrowser

import pandas as pd
import streamlit as st


def _try_read_csv(path):
    encodings = ("utf-8", "cp932", "shift_jis", "utf-16")
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    return None


def load_csv_files(path):
    """指定フォルダ内のCSVファイル一覧とデータフレームリストを返す。

    Returns:
        (list_of_paths, list_of_dataframes)
    """
    if not os.path.isdir(path):
        # フォルダが無ければ作成して空リストを返す（初回起動時などに親切）
        try:
            os.makedirs(path, exist_ok=True)
            st.info(f"指定されたフォルダがなかったため作成しました: {path}")
        except Exception as e:
            st.error(f"指定されたフォルダが存在しません: {path} ({e})")
            return [], []

    csv_files = sorted(glob.glob(os.path.join(path, "*.csv")))
    dataframes = []
    for csv_file in csv_files:
        df = _try_read_csv(csv_file)
        if df is None:
            st.error(f"CSVの読み込みに失敗しました: {csv_file}")
            dataframes.append(pd.DataFrame())
        else:
            dataframes.append(df)
    return csv_files, dataframes


def save_dataframe(df, csv_file):
    """DataFrame を csv_file に保存し、(success, message) を返す。

    ディレクトリを作成し、一時ファイル経由で書き出すことで
    書き込みの原子性と Windows での安全な置換を提供します。
    """
    tmp_path = None
    try:
        dirpath = os.path.dirname(csv_file)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(suffix=".tmp", dir=dirpath or None)
        os.close(fd)
        # pandas がファイルパスを受け取って書き出す
        df.to_csv(tmp_path, index=False)
        # 安全に置換
        os.replace(tmp_path, csv_file)
        return True, f"{os.path.basename(csv_file)} を保存しました。"
    except Exception as e:
        # 一時ファイルが残っていれば削除を試みる
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False, f"保存に失敗しました: {e}"


def open_urls(urls):
    """指定した URL リストを順に開く。"""
    for url in urls:
        try:
            if not url:
                continue
            webbrowser.open(url)
        except Exception as e:
            st.error(f"URLを開けませんでした: {url} ({e})")


def create_link_button(row):
    """pandas Series を受け取り、NAME/URL を使ってリンクボタンを作る。"""
    try:
        name = row.get("NAME") if "NAME" in row.index else str(row.name)
        url = row.get("URL", "")
        if pd.isna(url) or not url:
            st.write(name)
        else:
            # st.link_button が存在しない環境やバージョン差分に備えてフォールバック
            try:
                st.link_button(name, url, use_container_width=True)
            except Exception:
                # Markdown 形式で代替表示
                st.markdown(f"[{name}]({url})")
    except Exception as e:
        st.write(f"行の表示中にエラーが発生しました: {e}")
