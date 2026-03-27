---
name: all-test
description: 全てのテストを実行する。テストの実行を求められたときに使用する。
disable-model-invocation: true
allowed-tools: Bash(uv run pytest *), Bash(uv run ruff *), Bash(uv run pyright)
---

- pytestを実行: !`uv run pytest -v`
- ruffを実行: !`uv run ruff check .`
- pyrightを実行: !`uv run pyright`

全ての実行結果を確認し、失敗・エラーがあれば内容を報告してください。