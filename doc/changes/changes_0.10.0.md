# Script-Languages-Container-Tool 0.10.0, released 2022-04-04

Code name: Starter-script installation via Python

## Summary 

The main issue of this release is the new implementation of the start-script installation, which has been moved into the Python package (previously was implemented as bash scripts). The integration tests for the starter-scripts are now part of the regular Python-Unit-Tests (/test).
Also, Python 2 was removed from the Test-Container and the integration-test-docker-environment was increased to v0.9.0. Besides, there were two bug fixes.

## Features / Enhancements

 - #111: Remove Python2 in TestContainer
 - #117: Integrate integration-test-docker-environment 0.9.0
 - #121: Install starter-scripts via Python

## Bug Fixes

 - #109: fix starter scripts on GNU bash 4.2
 - #123: Fix error when running exaslct on a path containing spaces

## Documentation

 - #126: Prepared release 0.10.0

