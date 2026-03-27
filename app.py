import os

import streamlit as st

from streamlit_utils import load_csv_files, open_urls

st.set_page_config(page_title="web-launcher", page_icon="📂")


def create_link_button(row):
    """行データを受け取り、NAME/URL を使ってリンクボタンを作る。

    Args:
        row: 辞書型で NAME と URL のキーを含むことが期待される。

    Note:
        - URLが無いか空の場合は NAME のみをテキストとして表示
        - エラーが発生した場合はエラーメッセージを表示
    """
    name = row.get("NAME")
    if name is None:
        name = "Unknown"

    url = row.get("URL")
    if url is None or not url:
        st.write(name)
        return

    try:
        st.link_button(name, url, width="stretch")
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

    if "URL" not in df.columns:
        st.info("このCSVには 'URL' 列がありません。編集ページで確認してください。")
        return

    if st.button("全て開く", key=f"open_all_{selected}"):
        failed_urls = open_urls(df["URL"].drop_nulls().to_list())
        if failed_urls:
            st.warning(f"開けなかったURL: {failed_urls}")

    for row in df.iter_rows(named=True):
        create_link_button(row)


if __name__ == "__main__":
    main()
