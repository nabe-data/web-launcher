---
name: all-check
description: 全ての品質チェックを実行する。実装作業後に品質担保の目的で使用する。また「/all-check」で呼び出されたときに使用する。
---

- ruff・pytest・pyrightを実行: !`uv run ruff check .; uv run pytest -v; uv run pyright`

全ての実行結果を確認し、失敗・エラーがあれば修正を行ってください。修正が必要な場合は、修正後に再度全ての品質チェックを実行してください。