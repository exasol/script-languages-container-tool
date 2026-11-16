.. _user_guide:

User Guide
==========

.. toctree::
   :maxdepth: 1
   :hidden:

   build_and_export
   activate_slc
   partial_builds
   force_rebuild
   using_your_own_remote_cache
   running_tests
   report_package_updates
   delete_temporary_images

The User Guide explains the most important commands of the Script Languages
Container Tool or *SLCT* for short.

The examples use the script ``exaslct`` which is an alias for ``python3 -m
exasol.slc.tool.main`` and is installed together with the SLCT Python package.

The subcommands of ``exaslct`` deal with Script Languages Containers, or
*SLCs* for short.

Security
--------

Exasol version 8.19.0 and higher only accept TLS connections, which requires
``exaslct`` to access to the BucketFS via HTTPS. TLS by default includes
validating the TLS certificate, see `pyexasol documentation
<pyexasol_security_>`_ for a detailed explanation.

.. _pyexasol_security:
   https://exasol.github.io/pyexasol/master/user_guide/configuration/security.html

When using ``exaslct`` with Docker DB, please note, that Docker DB uses a
self-signed certificate, which cannot be validated against public certificate chains.

In this case you can disable the certificate validation by adding option
``--no-use-ssl-cert-validation`` to the resp. shell commands. However, this
should **NEVER** be used for production.
