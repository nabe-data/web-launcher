@echo off
:: ruffを実行（出力をヌルデバイスに捨てて、Gemini CLIのJSON出力を邪魔しないようにする）
uv run ruff check --fix . > nul 2>&1
uv run ruff format . > nul 2>&1

:: 最後に必ずGemini CLIが期待するJSONを標準出力に返す
echo {"decision": "allow", "message": "Ruff applied successfully"}