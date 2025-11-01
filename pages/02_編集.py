import os

import pandas as pd
import streamlit as st

from streamlit_utils import load_csv_files, save_dataframe

st.set_page_config(page_title="編集", page_icon="✏️")


def main():
    path = os.path.join(os.getcwd(), "user_data")
    csv_files, dfs = load_csv_files(path)

    # 保存によるリロード後に表示するトーストがセッションに残っていれば表示して消す
    if st.session_state.get("save_toast"):
        st.toast(st.session_state["save_toast"])
        del st.session_state["save_toast"]

    # 編集画面をメインに表示
    handle_edit_mode(path, csv_files, dfs)

    # 新規作成/アップロードUIはサイドバーに表示
    st.sidebar.write("CSVファイルを追加")
    handle_create_mode(path, container=st.sidebar)
    handle_upload_mode(path, container=st.sidebar)


def handle_edit_mode(path: str, csv_files: list, dfs: list) -> None:
    """CSVファイル編集用のUIを表示する。

    各CSVファイルに対して編集可能なデータエディタを表示し、保存ボタンを提供します。
    NAME/URL列が存在しない場合は自動的に追加します。

    Args:
        path: CSVファイルが格納されているディレクトリパス
        csv_files: CSVファイルパスのリスト
        dfs: 編集対象のDataFrameのリスト（csv_filesと順序対応）

    Note:
        - 保存成功時はトースト表示してページをリロード
        - 保存失敗時はエラーメッセージを表示
        - CSVファイルが無い場合は警告メッセージを表示
    """
    st.subheader("CSVファイルを編集")
    if not csv_files:
        st.warning(
            "CSVファイルが見つかりませんでした。編集画面から新規作成やアップロードが可能です。"
        )

    for csv_file, df in zip(csv_files, dfs):
        base = os.path.basename(csv_file)
        st.subheader(base)

        # 編集用に列がない場合は用意する
        if "NAME" not in df.columns:
            df.insert(0, "NAME", "")
        if "URL" not in df.columns:
            df["URL"] = ""

        edit_df = st.data_editor(
            df, num_rows="dynamic", use_container_width=True, key=f"editor_{base}"
        )

        if st.button("保存する", key=f"save_{base}"):
            success, msg = save_dataframe(edit_df, csv_file)
            if success:
                # 保存完了メッセージをセッションに入れてからリロードする（リロード後にトースト表示）
                st.session_state["save_toast"] = msg
                st.rerun()
            else:
                st.error(msg)


def handle_create_mode(path: str, container=st) -> None:
    """新規CSVファイル作成用のUIを表示する。

    Args:
        path: CSVファイルを作成するディレクトリパス
        container: UIを表示するStreamlitコンテナ。デフォルトはメイン領域

    Note:
        - 同名ファイルが存在する場合は作成せずにエラー表示
        - 作成成功時はトースト表示してページをリロード
        - 作成失敗時はエラーメッセージを表示
        - 新規ファイルには NAME, URL 列が自動的に追加される
    """
    # use a distinct key so sidebar/main inputs don't clash
    new_name = container.text_input("新規作成（例: new.csv）", key="create_new_name")
    if container.button("作成", key="create_button"):
        if new_name:
            save_path = os.path.join(path, new_name)
            if os.path.exists(save_path):
                container.error("同名ファイルが既に存在します。")
            else:
                new_df = pd.DataFrame(columns=["NAME", "URL"])
                success, msg = save_dataframe(new_df, save_path)
                if success:
                    st.session_state["save_toast"] = "新しいCSVファイルを追加しました"
                    st.rerun()
                else:
                    container.error(msg)
        else:
            container.error("ファイル名を入力してください。")


def handle_upload_mode(path: str, container=st) -> None:
    """CSVファイルアップロード用のUIを表示する。

    Args:
        path: アップロードしたCSVファイルを保存するディレクトリパス
        container: UIを表示するStreamlitコンテナ。デフォルトはメイン領域

    Note:
        - .csv 拡張子のファイルのみを受け付ける
        - アップロード成功時はトースト表示してページをリロード
        - CSVの読み込みやファイル保存に失敗した場合はエラーメッセージを表示
    """
    uploaded = container.file_uploader(
        "アップロード", type=["csv"], key="sidebar_upload"
    )
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded)
            save_path = os.path.join(path, uploaded.name)
            success, msg = save_dataframe(new_df, save_path)
            if success:
                st.session_state["save_toast"] = "CSVファイルをアップロードしました"
                st.rerun()
            else:
                container.error(msg)
        except Exception as e:
            container.error(f"アップロード中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
