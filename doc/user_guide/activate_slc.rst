Activating an SLC
=================

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
