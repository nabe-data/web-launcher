---
name: all-check
description: 全ての品質チェックを実行する。Pythonファイルの編集後や、「/all-check」で呼び出されたときに使用する。
---

- ruff・pytest・pyrightを実行: !`uv run ruff check .; uv run pytest -v; uv run pyright`

全ての実行結果を確認し、失敗・エラーがあれば内容を報告してください。