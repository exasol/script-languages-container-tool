# 3.5.0 - 2025-12-09

This release has several dependency updates, especially integration-test-docker-environment was updated to version 5.0.0.
Besides, there are some internal improvements.

## Security

 - Updated lock file

## Refactorings

 - #313: Updated GPU Test Query and updated Poetry dependencies and PTB GH action
 - #320: Updated poetry dependencies and Github workflows by PTB 1.12.0.
 - #328: Updated Github secrets for Docker credentials

## Dependencies

 - #327: Updated ITDE to 5.0.0

## Dependency Updates

### `main`
* Added dependency `click:8.2.1`
* Updated dependency `exasol-bucketfs:2.0.0` to `2.1.0`
* Updated dependency `exasol-integration-test-docker-environment:4.1.0` to `5.0.0`
* Updated dependency `jsonschema:4.24.0` to `4.25.1`
* Updated dependency `pydantic:2.11.7` to `2.12.5`

### `dev`
* Updated dependency `aiohttp:3.12.13` to `3.13.2`
* Updated dependency `exasol-toolbox:1.6.0` to `1.13.0`
* Added dependency `pyexasol:1.3.0`
