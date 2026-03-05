# 4.0.0 - 2026-03-05

## Summary

This major release uses a version 6.x of the Integration-Test-Docker-Environment, which encodes the platform tag (x86 or arm) into the docker image tags. This is a breaking change as existing docker images on Dockerhub won't be found anymore.
Furthermore, the Pydantic model for the CI.json was updated in order to support multiple different runners for building and testing SLCs, which is also a breaking change.
There is now a new command to generate a package difference report for two different Git versions (see User-Guide for more information).
The new package file format from https://github.com/exasol/script-languages-package-management is now added to the Docker build environment and considered for calculating the hashsum of the build-context.

## Features

 - #343: Migrated generate package diff tool to new package format
 - #344: Included new package file into docker build context

## Refactorings

 - #341: Updated integration-test-docker-environment
 - #197: Moved generate_package_diffs_for_flavors from script-languages to here
 - #346: Updated pydantic models to support ARM runners

## Documentation

 - Updated user-guide

## Dependency Updates

### `main`
* Updated dependency `click:8.2.1` to `8.3.1`
* Updated dependency `exasol-integration-test-docker-environment:5.0.0` to `6.1.0`
* Added dependency `exasol-script-languages-package-management:1.0.0`
* Removed dependency `importlib-metadata:8.7.1`
* Removed dependency `importlib-resources:6.5.2`
* Added dependency `pandas:2.3.3`
* Added dependency `tabulate:0.9.0`

### `dev`
* Added dependency `pandas-stubs:2.3.3.260113`
* Updated dependency `pytest-exasol-backend:1.2.4` to `1.3.0`
