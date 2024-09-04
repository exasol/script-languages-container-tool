# Script-Languages-Container-Tool 1.0.0, released 2024-09-04

Code name: Major refactoring and new deployment API

## Summary

This release changed the directory structure and aimed to separate the public and internal modules.
Also, the project now uses the `exasol-toolbox` to execute code quality CI jobs. There are new functions which
simplify the deployments of Script Language Containers on BucketFS.
The new API improves the generation of the Language Activation commands and provides new objects which contain
more detailed information about the installed Script Language Containers in BucketFS.

## Features

#218: Added an option to ignore certificate errors for upload command
#231: Extended LanguageDefinitionComponents

## Refactoring

#219: Replaced deprecated bucketfs API by new API
#171: Improved api generate_language_activation
#230: Created new method `deploy` with similar parameters as in python-extension-common
#234: Removed starter scripts
#237: Changed paths of package
