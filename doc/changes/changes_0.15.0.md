# Script-Languages-Container-Tool 0.15.0, released 2022-08-29

Code name: Initial API layer and support for stream output of tests to log files.

## Summary 

This release streams the output of running tests to the logfile during test execution. Also, a new API module 
has been added, which allows the usage of the script-languages-container-tools functionality from other Python packags.
Besides, there were some bugfixes and a minor improvement in the documentation in the code.

## Features / Enhancements

 - #160: Streamed test output to log file

## Refactorings

 - #124: Moved implementations of all click commands in separate methods

## Bug Fixes

 - #163: Fixed upload path if --path-in-bucket not specified
 - #164: Fixed default values for click parameters of type multiple=true

## Documentation

  - #152: Added note to exalsct scripts that these files are generated  
