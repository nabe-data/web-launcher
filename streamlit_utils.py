import glob
import os
import tempfile
import webbrowser
from typing import List, Optional, Tuple

import pandas as pd


def _try_read_csv(path: str) -> Optional[pd.DataFrame]:
    """CSVファイルを複数のエンコーディングで読み込みを試みます。

    Args:
        path: CSVファイルのパス

    Returns:
        pandas.DataFrame: 読み込みに成功した場合はDataFrame
        None: 全てのエンコーディングで読み込みに失敗した場合

    Note:
        以下のエンコーディングを順に試みます:
        - utf-8
        - shift_jis
    """
    encodings = ("utf-8", "shift_jis")
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except (UnicodeDecodeError, pd.errors.ParserError, Exception):
            continue
    return None


def load_csv_files(path: str) -> Tuple[List[str], List[pd.DataFrame]]:
    """指定フォルダ内のCSVファイル一覧とデータフレームリストを返す。

    Args:
        path: CSVファイルを探すディレクトリパス。

    Returns:
        tuple[list[str], list[pd.DataFrame]]:
            - list[str]: CSVファイルの絶対パスのリスト
            - list[pd.DataFrame]: 読み込んだDataFrameのリスト。読み込みに失敗した
              ファイルは空のDataFrameとなる

    Note:
        ディレクトリが存在しない場合、空のリストを返す。

        CSVファイルの読み込みは複数のエンコーディングを試みる。
        全て失敗した場合は空のDataFrameをリストに追加する。
    """
    if not os.path.isdir(path):
        return [], []

    csv_files = sorted(glob.glob(os.path.join(path, "*.csv")))
    dataframes: List[pd.DataFrame] = []
    for csv_file in csv_files:
        df = _try_read_csv(csv_file)
        dataframes.append(df if df is not None else pd.DataFrame())
    return csv_files, dataframes


def save_dataframe(df: pd.DataFrame, csv_file: str) -> Tuple[bool, str]:
    """DataFrame を csv_file に保存し、成功状態とメッセージを返す。

    ディレクトリを作成し、一時ファイル経由で書き出すことで
    書き込みの原子性と Windows での安全な置換を提供します。

    Args:
        df: 保存するDataFrame
        csv_file: 保存先のファイルパス。ディレクトリが存在しない場合は作成する

    Returns:
        tuple[bool, str]:
            - bool: 保存が成功したかどうか
            - str: 成功時は保存完了メッセージ、失敗時はエラーメッセージ

    Note:
        原子的な保存のため、一時ファイルに書き出してから目的のファイルに置換します。
        ファイルシステムの制限やパーミッションの問題で失敗する可能性があります。
        失敗時は一時ファイルを削除します。
    """
    tmp_path = None
    dirpath = os.path.dirname(csv_file)
    try:
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(suffix=".tmp", dir=dirpath or None)
        os.close(fd)
        df.to_csv(tmp_path, index=False)
        os.replace(tmp_path, csv_file)
        return True, f"{os.path.basename(csv_file)} を保存しました。"
    except Exception as e:
        return False, f"保存に失敗しました: {e}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                # 削除に失敗しても進行を妨げない
                pass


def open_urls(urls: List[str]) -> List[str]:
    """指定した URL リストを順に開く。

    Args:
        urls: 開くURLのリスト。

    Note:
        - 空のURLはスキップされる
        - 各URLはデフォルトのWebブラウザで開かれる
        - 開けなかったURLはリストとして返される

    Returns:
        list: 開けなかったURLのリスト
    """
    failed: List[str] = []
    for url in urls:
        if pd.isna(url):
            continue
        url_str = str(url).strip()
        if not url_str:
            continue
        try:
            webbrowser.open(url_str)
        except Exception:
            failed.append(url_str)
    return failed
