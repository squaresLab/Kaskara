.PHONY: check install test lint

lint:
	poetry run ruff check src
	poetry run mypy src

test:
	poetry run pytest

install:
	poetry install

check: lint test
