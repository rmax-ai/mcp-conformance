.PHONY: test lint format sync

sync:
	uv sync --dev

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/
