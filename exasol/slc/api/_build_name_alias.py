from __future__ import annotations

import warnings


def resolve_build_name(
    build_name: str | None,
    release_name: str | None,
) -> str | None:
    """
    Resolve the canonical build name while supporting the deprecated release-name alias.
    """
    if release_name is None:
        return build_name

    warnings.warn(
        "release_name is deprecated, use build_name instead",
        DeprecationWarning,
        stacklevel=3,
    )
    if build_name is not None:
        return build_name
    return release_name
