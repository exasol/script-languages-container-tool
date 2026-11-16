.. role:: var

Partial Builds and Rebuilds
===========================

During development or Continuous Integration you may want to limit the build
process to specific stages:

.. list-table::
   :header-rows: 1
   :widths: 15 20 20

   * -
     - Final stage (also called *goal*)
     - Initial stage
   * - CLI option
     - ``--goal``
     - ``--force-rebuild-from``
   * - Initial build
     - yes
     - no
   * - Consecutive rebuilds
     - yes
     - yes
   * - Includes stages
     - The specified depends on
     - Depending on the specified stage

Example for ``exaslct`` command ``build`` with option ``--goal``:

.. code:: shell

   exaslct build --flavor-path <path-to-flavor> --goal <build-stage>


.. note::

    * Command ``build`` only rebuilds the Docker images, but does not export a
      new SLC.
    * Option ``--goal`` is not supported for commands other than ``build`` and
      ``push`` as these require specific images.
    * Both options ``--goal`` and ``--force-rebuild-from`` can be used
      multiple times to specify multiple build stages.
    * Build stages before the one specified with CLI option
      ``--force-rebuild-from`` will use cached versions whenever possible.
      However, if a single stage is built, it will trigger a build for all following
      build stages.
    * The option ``--force-rebuild-from`` only has an effect when used with
      option ``--force-rebuild``.
    * When specifying a final stage :var:`<Sn>` with ``--goal`` then
      ``exaslct`` will first check if stages :var:`<Sn>` depends on, need
      to be updated.
    * When specifying an initial stage :var:`<S0>` with
      ``--force-rebuild-from`` then ``exaslct`` will also update all stages
      depending on :var:`<S0>`.

Please note :ref:`build_steps_and_their_dependencies`.

The following build stages are currently available:

* ``udfclient_deps``
* ``language_deps``
* ``build_deps``
* ``build_run``
* ``base_test_deps``
* ``base_test_build_run``
* ``flavor_test_build_run``
* ``flavor_base_deps``
* ``flavor_customization``
* ``release``
* ``security_scan``

.. code:: shell

   exaslct build \
        --flavor-path <path-to-flavor> \
        --force-rebuild \
        --force-rebuild-from <build-stage>
