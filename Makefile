TOP_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: tests
.SILENT: checks black isort mypy ruff pylint tests build release package publish

checks: black isort mypy ruff pylint

black:
	echo "- Running black (in check mode) ..."
	black --check src/jintonic

black-fix:
	echo "- Running black (in fix mode) ..."
	black src/jintonic

isort:
	echo "- Running isort (in check mode) ..."
	isort --check src/jintonic

isort-fix:
	echo "- Running isort (in fix mode) ..."
	isort src/jintonic

mypy:
	echo "- Running mypy ..."
	mypy --show-error-codes --check-untyped-defs src/jintonic

ruff:
	echo "- Running ruff ..."
	ruff src/jintonic

pylint:
	echo "- Running pylint ..."
	pylint --errors-only --output-format colorized src/jintonic

tests:
	echo "- Running doctests ..."
	pytest -c pyproject.toml --maxfail 1 --doctest-modules src/jintonic/

build: checks tests package

release: checks tests package publish

package:
	echo "- Building distribution ..."
	python -m build .

publish:
	echo "- Publishing distribution to PyPI ..."
	python -m twine upload -u $(PYPI_U) -p $(PYPI_P) dist/*
