import streamlit as st
import pandas as pd
import os
import glob
import webbrowser

def load_csv_files(path):
    """指定されたパスからCSVファイルを読み込み、データフレームのリストを返す。"""
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    dataframes = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            dataframes.append(df)
        except Exception as e:
            st.error(f"CSVファイルの読み込みに失敗しました: {csv_file} ({e})")
    return csv_files, dataframes

def open_urls(urls):
    """指定されたURLリストを順に開く。"""
    for url in urls:
        try:
            webbrowser.open(url)
        except Exception as e:
            st.error(f"URLを開くことができませんでした: {url} ({e})")

def create_link_button(row):
    """データフレームの行からリンクボタンを作成する。"""
    st.link_button(row['NAME'], row['URL'], use_container_width=True)

def save_dataframe(df, csv_file):
    """データフレームをCSVファイルとして保存する。"""
    try:
        df.to_csv(csv_file, index=False)
        st.success(f"{os.path.basename(csv_file)}を保存しました。")
    except Exception as e:
        st.error(f"保存中にエラーが発生しました: {e}")

def main():
    # st.title("ウェブサイト管理ツール")

    # フォルダ内のcsvファイルを読み込む
    # path = os.getcwd()
    path = os.path.join(os.getcwd(), "user_data")
    csv_files, dfs = load_csv_files(path)



    # サイドバーでファイル選択・編集切り替え
    sidebar_options = [os.path.basename(csv_file) for csv_file in csv_files] if csv_files else []
    sidebar_options.append('編集')
    selected = st.sidebar.radio('表示内容を選択', sidebar_options)

    if not csv_files:
        st.warning("CSVファイルが見つかりませんでした。編集画面から新規作成やアップロードが可能です。")

    if selected == '編集':
        st.header("CSVファイルの編集・追加・アップロード")
        for csv_file, df in zip(csv_files, dfs):
            st.subheader(os.path.basename(csv_file))
            edit_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            if st.button('保存する', key=f"save_{csv_file}"):
                save_dataframe(edit_df, csv_file)
                st.rerun()

        # CSVファイルの追加機能
        st.subheader("新しいCSVファイルの追加")
        new_csv_name = st.text_input("CSVファイル名（.csv拡張子を含む）")
        if st.button("新しいCSVファイルを追加"):
            if new_csv_name:
                save_path = os.path.join(path, new_csv_name)
                new_df = pd.DataFrame(columns=["NAME", "URL"])
                save_dataframe(new_df, save_path)
                st.rerun()
            else:
                st.error("CSVファイル名を入力してください。")

        # CSVファイルのアップロード機能
        uploaded_file = st.file_uploader("CSVファイルをアップロード", type=["csv"])
        if uploaded_file is not None:
            try:
                new_df = pd.read_csv(uploaded_file)
                new_csv_name = uploaded_file.name
                save_path = os.path.join(path, new_csv_name)
                save_dataframe(new_df, save_path)
                st.rerun()
            except Exception as e:
                st.error(f"アップロード中にエラーが発生しました: {e}")
    else:
        # ファイル閲覧画面
        idx = sidebar_options.index(selected)
        csv_file = csv_files[idx] if idx < len(csv_files) else None
        if csv_file is not None:
            df = dfs[idx]
            st.header(selected)
            if st.button('全て開く', key=f"open_all_{csv_file}"):
                open_urls(df['URL'])
            df.apply(create_link_button, axis=1)

if __name__ == "__main__":
    main()
