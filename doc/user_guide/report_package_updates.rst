Reporting Package Updates
=========================

Command ``generate-package-diffs`` reports which packages have been updated.

The report compares the flavors in directory ``flavors/`` of the current local
working copy to the latest Git tag.

Alternatively you can specify an arbitrary commit with CLI option
``--compare-to-commit``:

.. code:: shell

   exaslct generate-package-diffs \
        --current-working-copy-name "11.0.0" \
        --compare-to-commit "10.0.0" \
        --output-package-diff-directory docs/changes/package_diffs/11.0.0

The report includes the package categories:

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Package category
     - Included in the final release SLC?
   * - public
     - yes
   * - internal
     - no
