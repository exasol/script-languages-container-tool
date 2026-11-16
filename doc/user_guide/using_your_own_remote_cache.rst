Using Your Own Remote Cache
===========================

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
