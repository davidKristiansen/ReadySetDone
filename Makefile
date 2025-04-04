.PHONY: docs clean-docs

docs:
	uv pip install -r docs/requirements.txt || true
	uv run sphinx-build -b html docs/ docs/_build/html

clean-docs:
	rm -rf docs/_build
