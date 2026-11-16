Deleting Temporary Images
=========================

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
