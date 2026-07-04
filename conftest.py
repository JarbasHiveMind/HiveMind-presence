"""Top-level conftest.

hivescope ships the e2e fixtures and is a declared test dependency
(the [test] extra) — loaded unconditionally so a missing install fails
loudly instead of silently skipping the e2e suite.
"""
pytest_plugins = ["hivescope.pytest_fixtures"]
