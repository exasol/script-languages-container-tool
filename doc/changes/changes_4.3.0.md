# 4.3.0 - 2026-08-03

This release updates the integration-test-docker-environment to version 6.5.0 which fixes a bug when building the Script-Languages-Container with the "build_name" parameter. Also, the export command now allows to generate a symbolic link instead of a copy of the tar file.

## Features

* #382: Added parameter that export with export-path is creating a symlink instead copying

## Refactorings

* #391: Updated to ITDE 6.5.0

 

## Dependency Updates

### `main`

* Updated dependency `exasol-bucketfs:2.1.0` to `2.3.0`
* Updated dependency `exasol-integration-test-docker-environment:6.4.1` to `6.5.0`
