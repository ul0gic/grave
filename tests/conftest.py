"""Shared fixtures for the grave test suite.

grave is stateless — it creates no files and touches no database — so the
suite needs no storage isolation. The gh boundary is mocked per-test by
patching the API functions the CLI imports.
"""
