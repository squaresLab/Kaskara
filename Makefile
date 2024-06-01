.PHONY: all check install test lint

all: install check

lint:
	poetry run ruff check src
	poetry run mypy src

test:
	poetry run pytest

install:
	poetry install --with dev

postinstall:
	poetry run python -m kaskara.post_install

check: lint test
