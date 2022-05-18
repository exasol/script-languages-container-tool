# Script-Languages-Container-Tool 0.13.0, released 2022-05-18
2022-04-28
Code name: Update minimal supported Python version to 3.8

## Summary 

In this release, the  minimal supported python version is updated to 3.8. In the process, 
the integration-test-docker-environment is updated to version 0.11.0.
Additionally, an explicit dependency to importlib-resources is added, and permissions for docker credentials env file were fixed.

## Features / Enhancements

 n/a 

## Refactorings
 - #118: Updated minimal supported python version to 3.8 and Integrate integration-test-docker-environment 0.11.0

## Bug Fixes

 - #145: Added explicit dependency to importlib-resources 
 - #150: Fixed permissions for docker credentials env file

## Documentation

 - #144: Added documentation regarding installation of starter scripts and added contributing.md
 - #147: Improved short help messages
 - #155: Prepare release