---
name: all-test
description: 全てのテストを実行する。テストの実行を求められたときに使用する。
disable-model-invocation: true
allowed-tools: Bash(pytest *), Bash(ruff *), Bash(pyright)
---

- pytestを実行: !`pytest -v`
- ruffを実行: !`ruff check .`
- pyrightを実行: !`pyright`

全ての実行結果を確認し、失敗・エラーがあれば内容を報告してください。