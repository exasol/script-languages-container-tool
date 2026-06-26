import importlib.abc
from importlib.metadata import version

# Python 3.14 removed importlib.abc.Traversable (moved to importlib.resources.abc
# in 3.9). Patch it back so exasol-integration-test-docker-environment continues
# to work until it is updated upstream.
# See https://github.com/exasol/integration-test-docker-environment/issues/647.
if not hasattr(importlib.abc, "Traversable"):
    from importlib.resources.abc import Traversable as _Traversable  # type: ignore[import-not-found] # pylint: disable=import-error,no-name-in-module # fmt: skip
    importlib.abc.Traversable = _Traversable  # type: ignore[misc,attr-defined]
    del _Traversable

__version__ = version("exasol-script-languages-container-tool")
