import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from streamlit_utils import load_csv_files, save_dataframe

st.set_page_config(page_title="編集", page_icon="✏️")


def main():
    st.title("CSV編集・追加・アップロード")

    path = os.path.join(os.getcwd(), "user_data")
    csv_files, dfs = load_csv_files(path)

    # 保存によるリロード後に表示するトーストがセッションに残っていれば表示して消す
    if st.session_state.get("save_toast"):
        st.toast(st.session_state["save_toast"])
        del st.session_state["save_toast"]

    if not csv_files:
        st.warning("CSVファイルが見つかりませんでした。編集画面から新規作成やアップロードが可能です。")

    # 各CSVファイルごとに編集UIを出す
    for csv_file, df in zip(csv_files, dfs):
        base = os.path.basename(csv_file)
        st.subheader(base)

        # 編集用に列がない場合は用意する
        if 'NAME' not in df.columns:
            df.insert(0, 'NAME', '')
        if 'URL' not in df.columns:
            df['URL'] = ''

        edit_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"editor_{base}")

        if st.button("保存する", key=f"save_{base}"):
            success, msg = save_dataframe(edit_df, csv_file)
            if success:
                # 保存完了メッセージをセッションに入れてからリロードする（リロード後にトースト表示）
                st.session_state["save_toast"] = msg
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.subheader("新しいCSVファイルを作成")
    new_name = st.text_input("CSVファイル名（例: new.csv）")
    if st.button("作成"):
        if new_name:
            save_path = os.path.join(path, new_name)
            if os.path.exists(save_path):
                st.error("同名ファイルが既に存在します。")
            else:
                new_df = pd.DataFrame(columns=["NAME", "URL"])
                success, msg = save_dataframe(new_df, save_path)
                if success:
                    st.session_state["save_toast"] = "新しいCSVファイルを追加しました"
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.error("ファイル名を入力してください。")

    st.markdown("---")
    st.subheader("CSVファイルをアップロード")
    uploaded = st.file_uploader("CSVをアップロード", type=["csv"])
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded)
            save_path = os.path.join(path, uploaded.name)
            success, msg = save_dataframe(new_df, save_path)
            if success:
                st.session_state["save_toast"] = "CSVファイルをアップロードしました"
                st.rerun()
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"アップロード中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
