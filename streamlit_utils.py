import os
import glob
import pandas as pd
import webbrowser
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
        st.error(f"指定されたフォルダが存在しません: {path}")
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
    """DataFrame を csv_file に保存し、(success, message) を返す。"""
    try:
        df.to_csv(csv_file, index=False)
        return True, f"{os.path.basename(csv_file)} を保存しました。"
    except Exception as e:
        return False, f"保存に失敗しました: {e}"

def open_urls(urls):
    """指定した URL リストを順に開く。"""
    for url in urls:
        try:
            webbrowser.open(url)
        except Exception as e:
            st.error(f"URLを開けませんでした: {url} ({e})")

def create_link_button(row):
    """pandas Series を受け取り、NAME/URL を使ってリンクボタンを作る。"""
    try:
        name = row.get('NAME') if 'NAME' in row.index else str(row.name)
        url = row.get('URL', '')
        if pd.isna(url) or not url:
            st.write(name)
        else:
            st.link_button(name, url, use_container_width=True)
    except Exception as e:
        st.write(f"行の表示中にエラーが発生しました: {e}")
