# 4.4.0 - 2026-09-21

## Summary

This release improves security by updating vulnerable dependencies, switches BucketFS access to HTTPS,
and adds support for running SLC database tests with pytest.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| gitpython | PYSEC-2026-3984 | 3.1.57 | 3.1.60 |
| gitpython | PYSEC-2026-3982 | 3.1.57 | 3.1.60 |
| gitpython | PYSEC-2026-3783 | 3.1.57 | 3.1.58 |
| gitpython | PYSEC-2026-3785 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3786 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3783 | 3.1.57 | 3.1.58 |
| gitpython | PYSEC-2026-3787 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3788 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3784 | 3.1.57 | 3.1.58 |
| gitpython | PYSEC-2026-3786 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3787 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3788 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3840 | 3.1.57 | 3.1.58 |
| gitpython | PYSEC-2026-3838 | 3.1.57 | 3.1.58 |
| gitpython | PYSEC-2026-3841 | 3.1.57 | 3.1.58 |
| gitpython | PYSEC-2026-3837 | 3.1.57 | 3.1.59 |
| gitpython | PYSEC-2026-3843 | 3.1.57 | 3.1.58 |
| tornado | PYSEC-2026-3928 | 6.5.7 | 6.5.8 |
| tornado | GHSA-wwv5-g3v4-889x | 6.5.7 | 6.5.8 |
| tornado | GHSA-8423-8fgw-73vq | 6.5.7 | 6.5.8 |

## Features

* #404: Use HTTPS for BucketFS access (HTTP access is deprecated)
* #401: Added support for running SLC database tests with pytest

## Dependency Updates

### `main`

* Updated dependency `click:8.4.2` to `8.5.0`
* Updated dependency `pydantic:2.13.4` to `2.13.5`

### `dev`

* Updated dependency `exasol-toolbox:10.4.0` to `10.5.0`
* Updated dependency `tqdm:4.70.0` to `4.70.1`
