.. role:: var

.. _user_guide:

User Guide
==========

The User Guide explains the most important commands of the Script Languages
Container Tool or *SLCT* for short.

The examples use the script ``exaslct`` which is an alias for ``python3 -m
exasol.slc.tool.main`` and is installed together with the SLCT Python package.

The subcommands of ``exaslct`` deal with Script Languages Containers, or
*SLCs* for short.

Building and Exporting an SLC
-----------------------------

Build the SLC and export it to the local file system

.. code:: shell

   exaslct export --flavor-path flavors/<flavor-name> --export-path <export-path>

or deploy it directly:

.. code:: shell

   exaslct deploy \
       --flavor-path flavors/<flavor-name> \
       --bucketfs-host <hostname-or-ip> \
       --bucketfs-port <port> \
       --bucketfs-user w \
       --bucketfs-password <password>  \
       --bucketfs-name <bucketfs-name> \
       --bucket <bucket-name> \
       --path-in-bucket <path/in/bucket>

After successful deployment, the command will display the activation
statement, see details in the next section.

Activating an SLC
-----------------

After deployment, the SLC needs to be *activated* by setting a *language
alias*.  The activation can be applied to one of the following scopes:

.. list-table::
   :header-rows: 1
   :widths: 20 90

   * - Scope
     - Description
   * - ``ALTER SESSION``
     - Limited to the current session
   * - ``ALTER SYSTEM``
     - Persistent for the entire database system

Execute the generated SQL statement in your database session to activate the
SLC.

If you uploaded a container manually, you can display the activation statement
with

.. code:: shell

   exaslct generate-language-activation \
        --flavor-path flavors/<flavor-name> \
        --bucketfs-name <bucketfs-name> \
        --bucket-name <bucket-name> \
        --path-in-bucket <path/in/bucket> \
        --container-name <container-name>

``<container-name>`` is the name of the uploaded archive without its file
extension ``.tar.gz``.

Example Output
~~~~~~~~~~~~~~

The activation statement looks like:

.. code:: shell

   ALTER SESSION SET SCRIPT_LANGUAGES='<LANGUAGE_ALIAS>=localzmq+protobuf:///<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>?lang=<language>#buckets/<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>/exaudf/exaudfclient[_py3]';

``<language>`` is defined by the flavor in file ``language_definition``,
e.g. for flavor `standard-EXASOL-all-python-3.12 <py312-flavor_>`_.

.. _py312-flavor: https://github.com/exasol/script-languages-release/blob/master/flavors/standard-EXASOL-all-python-3.12/flavor_base/language_definition

Forcing a Rebuild
-----------------

You can force rebuilding the SLC with CLI option ``--force-rebuild`` for most
commands of ``exaslct``, except ``clean``.  This is helpful for fixing bugs
and security vulnerabilities by updating the dependencies.

Partial Builds and Rebuilds
---------------------------

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

Using Your Own Remote Cache
---------------------------

``exaslct`` caches Docker images locally and remotely. For remote caching
``exaslct`` uses Docker Hub by default.

With the following CLI options you can use an alternate Docker registry for
``exaslct`` commands that could trigger a build, incl. ``build``, ``export``,
``upload``, and ``run-db-test``:

* ``--source-docker-repository-name``
* ``--source-docker-tag-prefix``
* ``--source-docker-username``
* ``--source-docker-password``

There are corresponding options for the Docker registry to upload images with
``exaslct push``:

* ``--target-docker-repository-name``
* ``--target-docker-tag-prefix``
* ``--target-docker-username``
* ``--target-docker-password``

The following command line specifies the repository name:

.. code:: shell

   exaslct export \
       --flavor-path <path-to-flavor> \
       --source-docker-repository-name \
         <hostname>[:<port>]/<user>/<repository-name>

Running Tests
-------------

Running Tests Using a Flavor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following command runs the tests with an SLC built from the specified flavor:

.. code:: shell

   exaslct run-db-test --flavor-path flavors/<flavor-name>

.. important::

   You need to run the Docker container in `privileged <privileged_mode_>`_ mode to execute the
   tests.

.. _privileged_mode: https://docs.docker.com/reference/cli/docker/container/run/#privileged

Running Tests Using a Pre-Built SLC
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can test a pre-built SLC file (``*.tar.gz``) with the following command:

.. code:: shell

   exaslct run-db-test \
        --flavor-path flavors/<flavor-name> \
        --use-existing-container <path-to-file>

With option ``--use-existing-container``, ``exaslct`` doesn't build and export
the container which is significantly faster.

.. note::

    1. ``exaslct`` does not check if the specified SLC file is compatible to
       the specified flavor. Incompatibilities can make the tests fail.

    2. Options ``--reuse-uploaded-container`` and ``--reuse-test-environment``
       will still upload new files to BucketFS but ignore updated files as
       ``exaslct`` cannot identify updates.

Running Tests With Hardware Acceleration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your test environment has a supported hardware accelerator, you can use
the accelerator when running the tests.  Currently, only ``nvidia`` is
supported. The following command launches the docker-db with enabled
``NVIDIA`` accelerator:

.. code:: shell

   exaslct run-db-test \
        --flavor-path flavors/<flavor-name> \
        --accelerator nvidia

Reporting Package Updates
-------------------------

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

Deleting Temporary Images
-------------------------

Building an SLC creates or downloads multiple Docker images which can consume
a great amount of disk space. Therefore, we recommend removing the Docker
images of a flavor after working with them.

The following command deletes all images of the specified flavor:

.. code:: shell

   exaslct clean-flavor-images --flavor-path flavors/<flavor-name>

The following command deletes all images of all flavors:

.. code:: shell

   exaslct clean-all-images

.. note::

    ``clean-all-images`` does not delete the Linux image that is used as the base
    for the images built in previous steps. Furthermore, this
    ``clean-all-images`` doesn’t delete *cached* files in the output
    directory. The default path for the output directory is ``.build_output``.
