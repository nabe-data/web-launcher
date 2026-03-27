# ruffを実行（出力を捨てる）
uv run ruff check --fix . *> $null
uv run ruff format . *> $null

# Gemini CLI向けにJSONを標準出力
Write-Output '{"decision": "allow", "message": "Ruff applied successfully"}'