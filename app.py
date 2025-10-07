import os

import streamlit as st

from streamlit_utils import create_link_button, load_csv_files, open_urls

st.set_page_config(page_title="web-launcher", page_icon="📂")


def main():
    path = os.path.join(os.getcwd(), "user_data")
    csv_files, dfs = load_csv_files(path)

    if not csv_files:
        st.warning(
            "CSVファイルが見つかりませんでした。編集ページで新規作成やアップロードが可能です。"
        )
        return

    sidebar_options = [os.path.basename(p) for p in csv_files]
    selected = st.sidebar.radio("表示するファイルを選択", sidebar_options)

    try:
        idx = sidebar_options.index(selected)
    except ValueError:
        st.error("選択したファイルが見つかりません。")
        return

    df = dfs[idx]
    st.header(selected)

    if "URL" in df.columns:
        if st.button("全て開く", key=f"open_all_{selected}"):
            open_urls(df["URL"].dropna().tolist())
        df.apply(create_link_button, axis=1)
    else:
        st.info("このCSVには 'URL' 列がありません。編集ページで確認してください。")


if __name__ == "__main__":
    main()
