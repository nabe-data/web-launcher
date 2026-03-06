import os

import pandas as pd
import streamlit as st

from streamlit_utils import load_csv_files, open_urls

st.set_page_config(page_title="web-launcher", page_icon="📂")


def create_link_button(row):
    """pandas Series を受け取り、NAME/URL を使ってリンクボタンを作る。

    Args:
        row: pandas.Series で NAME と URL の列を含むことが期待される。
            NAME が無い場合は行インデックスを使用

    Note:
        - URLが無いか空の場合は NAME のみをテキストとして表示
        - エラーが発生した場合はエラーメッセージを表示
    """
    name = row.get("NAME", None)
    if pd.isna(name) or name is None:
        name = str(row.name)

    url = row.get("URL", "")
    if pd.isna(url) or not url:
        st.write(name)
        return

    try:
        st.link_button(name, url, use_container_width=True)
    except Exception as e:
        st.write(f"行の表示中にエラーが発生しました: {e}")


def main():
    path = os.path.join(os.getcwd(), "user_data")
    # user_data フォルダが無ければ作成しておく（編集/アップロード時に必要）
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        st.warning(f"user_data ディレクトリの作成に失敗しました: {e}")
    csv_files, dfs = load_csv_files(path)

    if not csv_files:
        st.warning(
            "CSVファイルが見つかりませんでした。編集ページで新規作成やアップロードが可能です。"
        )
        return

    sidebar_options = [os.path.basename(p) for p in csv_files]
    selected = st.sidebar.radio("表示するファイルを選択", sidebar_options)

    idx = sidebar_options.index(selected)
    df = dfs[idx]
    st.header(selected)

    if "URL" in df.columns:
        if st.button("全て開く", key=f"open_all_{selected}"):
            failed_urls = open_urls(df["URL"].dropna().tolist())
            if failed_urls:
                st.warning(f"開けなかったURL: {failed_urls}")

        for _, row in df.iterrows():
            create_link_button(row)
    else:
        st.info("このCSVには 'URL' 列がありません。編集ページで確認してください。")


if __name__ == "__main__":
    main()
