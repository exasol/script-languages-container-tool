# 4.5.0 - 2026-11-18

## Summary

This release updates the README and the user guide by removing duplicated parts and shortening explanations as much as possible.

The update focused on consistency regarding:

* Deviations from the actual implementation
* Terminology
* Phrasing
* Formatting

This release also raises the minimum supported Python version to 3.11.5 and updates `exasol-script-languages-package-management` to version 2.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| aiohttp | PYSEC-2026-4366 | 3.14.3 | 3.14.4 |
| aiohttp | PYSEC-2026-4365 | 3.14.3 | 3.14.4 |
| aiohttp | PYSEC-2026-4368 | 3.14.3 | 3.14.4 |
| aiohttp | PYSEC-2026-4369 | 3.14.3 | 3.14.4 |
| aiohttp | PYSEC-2026-4370 | 3.14.3 | 3.14.4 |
| aiohttp | PYSEC-2026-4367 | 3.14.3 | 3.14.4 |
| aiohttp | PYSEC-2026-4371 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-123817 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128129 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128132 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128130 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128127 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128128 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128131 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128126 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128125 | 3.14.3 | 3.14.4 |
| aiohttp | CVE-2026-128124 | 3.14.3 | 3.14.4 |
| black | CVE-2026-114134 | 26.5.1 | 26.10.1 |
| certifi | PYSEC-2026-4320 | 2026.7.22 | 2026.10.18 |
| certifi | PYSEC-2026-4320 | 2026.7.22 | 2026.10.18 |
| filelock | CVE-2026-112940 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112913 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112907 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112938 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112936 | 3.32.7 | 4.0.9 |
| filelock | CVE-2026-112910 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112909 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112911 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112939 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112915 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112935 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112912 | 3.32.7 | 4.2.1 |
| filelock | CVE-2026-112908 | 3.32.7 | 4.2.1 |
| gitpython | CVE-2026-114145 | 3.1.62 | 3.2.1 |
| gitpython | CVE-2026-110859 | 3.1.62 | 3.2.0 |
| gitpython | CVE-2026-110858 | 3.1.62 | 3.2.0 |
| gitpython | CVE-2026-110856 | 3.1.62 | 3.2.0 |
| gitpython | CVE-2026-110857 | 3.1.62 | 3.2.0 |
| gitpython | CVE-2026-110855 | 3.1.62 | 3.2.0 |
| msgpack | CVE-2026-114613 | 1.2.2 | 1.2.3 |
| multidict | PYSEC-2026-4244 | 6.9.0 | 6.9.1 |
| pyasn1 | CVE-2026-119196 | 0.6.4 | 0.6.5 |
| pyasn1 | CVE-2026-119194 | 0.6.4 | 0.6.5 |
| pyasn1 | CVE-2026-119197 | 0.6.4 | 0.6.5 |
| pyasn1 | CVE-2026-119195 | 0.6.4 | 0.6.5 |
| pylint | CVE-2026-114608 | 4.0.8 | 4.0.9 |
| soupsieve | CVE-2026-126192 | 2.9.2 | 2.10.0 |
| soupsieve | CVE-2026-126193 | 2.9.2 | 3.0.2 |
| soupsieve | CVE-2026-126191 | 2.9.2 | 3.0.2 |
| tornado | CVE-2026-116577 | 6.5.10 | 6.6 |
| tornado | CVE-2026-115927 | 6.5.10 | 6.6 |
| tornado | CVE-2026-116578 | 6.5.10 | 6.6 |
| virtualenv | PYSEC-2026-4382 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4374 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4376 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4380 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4375 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4383 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4373 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4384 | 21.9.0 | 21.14.7 |
| virtualenv | PYSEC-2026-4372 | 21.9.0 | 21.14.10 |
| virtualenv | PYSEC-2026-4377 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4381 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4378 | 21.9.0 | 21.14.9 |
| virtualenv | PYSEC-2026-4386 | 21.9.0 | 21.14.2 |
| virtualenv | PYSEC-2026-4387 | 21.9.0 | 21.14.2 |
| virtualenv | PYSEC-2026-4385 | 21.9.0 | 21.14.4 |
| virtualenv | PYSEC-2026-4379 | 21.9.0 | 21.14.9 |

## Refactorings

* Removed support for Python 3.10, the minimum supported version is now 3.11.5

## Dependency Updates

### `main`

* Updated dependency `exasol-bucketfs:2.3.0` to `2.3.1`
* Updated dependency `exasol-script-languages-package-management:1.3.1` to `2.0.0`
* Updated dependency `pydantic:2.13.5` to `2.14.2`

### `dev`

* Updated dependency `aiohttp:3.14.3` to `3.14.5`

## Documentation

* #414: Updated documentation
* #421: Added SSL advisory to the user guide
* #426: Updated SSL advisory in the user guide