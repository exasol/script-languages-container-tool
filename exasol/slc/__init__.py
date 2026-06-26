import importlib.abc
import multiprocessing
import sys
from importlib.metadata import version

# Python 3.14 removed importlib.abc.Traversable (moved to importlib.resources.abc
# in 3.9). Patch it back so exasol-integration-test-docker-environment continues
# to work until it is updated upstream.
# See https://github.com/exasol/integration-test-docker-environment/issues/647.
if not hasattr(importlib.abc, "Traversable"):
    # isort: off
    from importlib.resources.abc import Traversable as _Traversable  # type: ignore[import-not-found] # pylint: disable=import-error,no-name-in-module # fmt: skip
    importlib.abc.Traversable = _Traversable  # type: ignore[misc,attr-defined]
    del _Traversable

# Python 3.14 changes the default multiprocessing start method on Linux to
# forkserver, which breaks Luigi's parallel task execution (workers share
# module-level state that forkserver/spawn workers don't inherit, and
# dynamically-loaded task classes aren't picklable across a spawn boundary).
# This must be set here rather than in main.py so it also applies when the
# API is used directly (e.g. integration tests) rather than via the CLI.
if sys.platform == "linux":
    multiprocessing.set_start_method("fork", force=True)

__version__ = version("exasol-script-languages-container-tool")
