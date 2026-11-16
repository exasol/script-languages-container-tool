Running Tests
=============

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
