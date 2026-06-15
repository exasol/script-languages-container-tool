# 4.1.0 - 2026-06-15

## Summary

Use build name for docker image and archive names when specified and fix the generation of package diff.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| aiohttp | CVE-2026-34515 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34513 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34516 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34517 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34519 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34518 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34520 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34525 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-22815 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34514 | 3.13.3 | 3.13.4 |
| aiohttp | CVE-2026-34993 | 3.13.3 | 3.14.0 |
| aiohttp | CVE-2026-47265 | 3.13.3 | 3.14.0 |
| black | CVE-2026-32274 | 25.12.0 | 26.3.1 |
| cryptography | PYSEC-2026-35 | 46.0.5 | 46.0.6 |
| cryptography | PYSEC-2026-36 | 46.0.5 | 46.0.7 |
| cryptography | PYSEC-2026-36 | 46.0.5 | 46.0.7 |
| cryptography | PYSEC-2026-35 | 46.0.5 | 46.0.6 |
| gitpython | CVE-2026-42215 | 3.1.46 | 3.1.47 |
| gitpython | CVE-2026-42284 | 3.1.46 | 3.1.47 |
| gitpython | CVE-2026-44244 | 3.1.46 | 3.1.49 |
| gitpython | GHSA-mv93-w799-cj2w | 3.1.46 | 3.1.50 |
| idna | CVE-2026-45409 | 3.11 | 3.15 |
| pip | PYSEC-2026-196 | 26.0.1 | 26.1.2 |
| pip | CVE-2026-3219 | 26.0.1 | 26.1 |
| pip | CVE-2026-6357 | 26.0.1 | 26.1 |
| pyasn1 | CVE-2026-30922 | 0.6.2 | 0.6.3 |
| pygments | CVE-2026-4539 | 2.19.2 | 2.20.0 |
| pytest | CVE-2025-71176 | 8.4.2 | 9.0.3 |
| requests | CVE-2026-25645 | 2.32.5 | 2.33.0 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| tornado | PYSEC-2026-140 | 6.5.4 | 6.5.5 |
| tornado | PYSEC-2026-140 | 6.5.4 | 6.5.5 |
| tornado | GHSA-78cv-mqj4-43f7 | 6.5.4 | 6.5.5 |
| tornado | CVE-2026-35536 | 6.5.4 | 6.5.5 |
| tornado | CVE-2026-49854 | 6.5.4 | 6.5.6 |
| urllib3 | PYSEC-2026-142 | 2.6.3 | 2.7.0 |
| urllib3 | PYSEC-2026-142 | 2.6.3 | 2.7.0 |
| urllib3 | PYSEC-2026-141 | 2.6.3 | 2.7.0 |

## Bugs

 - #367: Fixed gen_package_diff
 - #377: Use build_name for docker images and archives and unify build_name and release_name
 - #375: Keep `var/lib/dpkg` in exported container archives for SBOM generation

## Internal

 - Updated PTB to version 8.2.0

## Dependency Updates

### `main`

* Updated dependency `click:8.3.1` to `8.4.1`
* Updated dependency `exasol-bucketfs:2.1.0` to `2.2.0`
* Updated dependency `exasol-integration-test-docker-environment:6.1.0` to `6.2.0`
* Updated dependency `exasol-script-languages-package-management:1.0.0` to `1.3.0`
* Updated dependency `pydantic:2.12.5` to `2.13.4`
* Updated dependency `tabulate:0.9.0` to `0.10.0`

### `dev`

* Updated dependency `aiohttp:3.13.3` to `3.14.1`
* Updated dependency `exasol-toolbox:5.1.1` to `8.2.0`
* Updated dependency `pytest-exasol-backend:1.3.0` to `1.4.1`
* Updated dependency `tqdm:4.67.3` to `4.68.2`