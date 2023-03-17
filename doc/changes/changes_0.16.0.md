# Script-Languages-Container-Tool 0.15.0, released 2022-08-29

Code name: Path-in-bucket parameter fix, initial API layer and support for stream output of tests to log files.

## Summary 

This release fixes a major bug which occured if the parameter "path-in-bucket" was not specified.
Also, it introduces a new API module , which allows the usage of the script-languages-container-tools functionality from other Python packages.
The handling of the logging for tests has been improved, as the logs are now written to the log-file during the test execution.
Besides, there is one more bugfix and a minor improvement in the documentation in the code.

## Features / Enhancements

 - #160: Streamed test output to log file
 - #175: Update vagrant environment

## Refactorings

 - #124: Moved implementations of all click commands in separate methods

## Bug Fixes

 - #163: Fixed upload path if --path-in-bucket not specified
 - #164: Fixed default values for click parameters of type multiple=true
 - #174: Add missing PYTHON3 to the add_missing_builtin option for the LanguageDefinition class
 - 
## Documentation

  - #152: Added note to exalsct scripts that these files are generated  
