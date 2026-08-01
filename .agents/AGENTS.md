# Role & Language
- ユーザーとのやり取りは、Planモードの出力も含めすべて**日本語**で行ってください。
- 専門用語については、必要に応じて英語を併記してください。

# Environment & Tools
- Python関連のコマンド（pytest, ruff, pyrightなど）を実行する際は、必ず `uv run` を介して実行してください。
- 例: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

# Rules
- 実装を行った後には、必ず以下2つのskillsを実行してください。
  - コードのシンプル化: /staged-simplifier
  - 品質チェック: /all-check
