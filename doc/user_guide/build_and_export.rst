Building and Exporting an SLC
=============================

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
