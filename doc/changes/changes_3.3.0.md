# 3.3.0 - 2025-06-02

This release aims to avoid leakage of security credentials in log files. Also, it updates the Python dependencies.
## Security

 - #293: Updated poetry dependencies
   * Fixed CVE-2025-47287 in transitive productive dependency `tornado` via `luigi` by updating `tornado` to version `6.5.1`
   * Fixed CVE-2025-47273 in transitive dev dependency `setuptools` via `exasol-toolbox`, `bandit`, `stevedore` by updating `setuptools` to version `80.9.0`

## Refactorings

 - #296: Reformat code with latest PTB
 - #295: Do not write docker password to test_output file
