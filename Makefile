.PHONY: help install install-dev format lint check test clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make format         - Format code with Ruff"
	@echo "  make lint           - Lint code with Ruff (check only)"
	@echo "  make check          - Run both linting and formatting checks"
	@echo "  make fix            - Auto-fix linting issues with Ruff"
	@echo "  make test           - Run tests with pytest"
	@echo "  make clean          - Remove cache files"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

format:
	uv run ruff format .

lint:
	uv run ruff check .

check:
	uv run ruff check .
	uv run ruff format --check .

fix:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
