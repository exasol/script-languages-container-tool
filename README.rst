Script-Languages-Container-Tool
===============================

.. image:: https://github.com/exasol/script-languages-container-tool/actions/workflows/main.yml/badge.svg?branch=main
     :target: https://github.com/exasol/script-languages-container-tool/actions/workflows/ci.yml
     :alt: Checks main

.. image:: https://img.shields.io/pypi/dm/exasol-script-languages-container-tool
     :target: https://pypi.org/project/exasol-script-languages-container-tool/
     :alt: Downloads

.. image:: https://img.shields.io/pypi/v/exasol-script-languages-container-tool
     :target: https://pypi.org/project/exasol-script-languages-container-tool/
     :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/exasol-script-languages-container-tool
    :target: https://pypi.org/project/exasol-script-languages-container-tool
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Formatter - Black

.. image:: https://img.shields.io/badge/imports-isort-ef8336.svg
    :target: https://pycqa.github.io/isort/
    :alt: Formatter - Isort

.. image:: https://img.shields.io/pypi/l/exasol-script-languages-container-tool
     :target: https://opensource.org/license/MIT
     :alt: License

.. image:: https://img.shields.io/github/last-commit/exasol/script-languages-container-tool
     :target: https://github.com/exasol/script-languages-container-tool
     :alt: Last Commit

Overview
--------

The Script-Languages-Container-Tool (*SLCT* for short) provides the shell
command ``exaslct`` to build script language containers (SLCs). You can build,
export and upload SLCs from so-called *flavors* containing the detailed build
instructions. You can find pre-defined flavors in GitHub repository
`script-languages-release
<https://github.com/exasol/script-languages-release>`__. The repository also
describes how you can customize these flavors.

Prerequisites
-------------

.. note::

   Since version 1.0.0 the so-called *starter scripts* are removed.  In older
   versions of SLCT the starter scripts pulled the ``exaslct`` Docker
   container runtime.

   If you can’t use Python3, you still can use our `AI-lab
   <https://github.com/exasol/ai-lab>`__ providing VM images, AMI images, and
   a Docker image, all capable of building SLCs.

For running
~~~~~~~~~~~

In order to use this tool, your system needs to fulfill the following
prerequisites:

* Software

  * Linux
  * Python3 >= 3.10
  * `Docker <https://docs.docker.com/>`__ >= 17.05

    * with support for `multi-stage builds
      required <https://docs.docker.com/build/building/multi-stage/>`__
    * host volume mounts need to be allowed

* System Setup

  * We recommend at least 50 GB free disk space on the partition where
    Docker stores its images, on linux Docker typically stores the
    images at ``/var/lib/docker``.
  * For the partition where the output directory (default:
    ``./.build_output``) is located we recommend additionally at least 10 GB
    free disk space.

Further, prerequisites might be necessary for specific tasks. These are
listed under the corresponding section.

Installation
------------

In general, it’s good practice to install the package in a virtual
environment, using ``venv`` or ``Poetry``.

Pip via PyPI
~~~~~~~~~~~~

.. code:: bash

   python3 -m pip install exasol-script-languages-container-tool

Pipx via PyPI
~~~~~~~~~~~~~

If you plan to use ``exasol-script-languages-container-tool`` on the
command line only via the ``exaslct`` script, we suggest the
installation via ``pipx``:

.. code:: bash

   pipx install exasol-script-languages-container-tool

Usage
-----

See `User Guide <https://exasol.github.io/script-languages-container-tool/main/user_guide/user_guide.html>`__.

Features
--------

- Build a script language container as Docker images
- Export a script language container as an archive which can be used for
  extending Exasol UDFs
- Upload a script language container as an archive to the Exasol DB’s
  BucketFS
- Generating the activation command for a script language container
- Can use Docker registries, such as Docker Hub, as a cache to avoid
  rebuilding image without changes
- Can push Docker images to Docker registries
- Run tests for your container against an Exasol DB (docker-db or
  external db)


📚 Documentation
----------------

For further details, check out latest `documentation <https://exasol.github.io/script-languages-container-tool>`__.
