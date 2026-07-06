# We're using Make as a command runner, so always make (avoids need for .PHONY)
MAKEFLAGS += --always-make

help:  # Display help
	@echo "Usage: make [target] [ARGS='additional args']\n\nTargets:"
	@awk -F'#' '/^[a-z0-9-]+:/ { sub(":.*", "", $$1); print " ", $$1, "#", $$2 }' Makefile | column -t -s '#'

all: lint unit  # Run linting and unit tests

# Please keep the list below in alphabetical order.

fix:  # Auto-fix linting issues
	uv run --group lint ruff check --fix --preview
	uv run --group lint ruff format --preview

format:  # Format the Python code
	uv run --group lint ruff format --preview

integration:  # Run integration tests via spread, for example: make integration ARGS='-debug'
	spread -v $(ARGS)

lint:  # Perform linting, spell checking, and static type checks
	uv run --locked --group lint ruff check --preview
	uv run --locked --group lint ruff format --preview --check
	uv run --locked --group lint codespell $(ARGS)
	uv run --locked --group lint --group unit ty check $(ARGS)

unit:  # Run unit tests, for example: make unit ARGS='tests/unit/test_evaluate.py::test_check_charm_name'
	uv run --locked --group unit coverage run --source=. --branch -m pytest -v --tb native $(ARGS)
	uv run --locked --group unit coverage report
