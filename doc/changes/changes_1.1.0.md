# 1.1.0 - 2025-01-29

Code name: Language Definition and Export optimization

## Summary

This release optimizes the export step to minimize disk space. Also, it adds support for the `language_definitions.json`. Besides this it also contains some refactorings.

## Features

 - #245: Implemented support for Json for language definition
 - #263: Extended language_definitions.json with deprecation fields

## Refactoring

 - #254: Replaced `set-output` GH command and updated Python Toolbox and ITDE
 - #257: Updated formating rules
 - #256: Fixed type hints
 - #358: Minimize disk space during export
 - #253: Fixed help text for exaslct

## Documentation

 - #243: Removed incomplete title in user guide
