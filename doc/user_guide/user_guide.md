# Script-Languages-Container-Tool User Guide

## Table of Contents

1. [How to build an existing flavor?](#how-to-build-an-existing-flavor)
2. [How to activate a script language container in the database](#how-to-activate-a-script-language-container-in-the-database)
3. [Force a rebuild](#force-a-rebuild)
4. [Partial builds or rebuilds](#partial-builds-and-rebuilds)
5. [Using your own remote cache](#using-your-own-remote-cache)
6. [Testing an existing flavor](#testing-an-existing-flavor)
7. [Cleaning up after your are finished](#cleaning-up-after-you-are-finished)

## Starter script

For simplicity the following examples use the script version (`exaslct`), which will be installed together with the Python package. The script is just an alias for `python3 -m exasol.slc.tool.main`.

## How to build an existing flavor?

Create the language container and export it to the local file system

```bash
exaslct export --flavor-path=flavors/<flavor-name> --export-path <export-path>
```

or upload it directly into the BucketFS (currently http only, https follows soon)

```bash
exaslct upload --flavor-path=flavors/<flavor-name> --database-host <hostname-or-ip> --bucketfs-port <port> \
                   --bucketfs-username w --bucketfs-password <password>  --bucketfs-name <bucketfs-name> \
                   --bucket-name <bucket-name> --path-in-bucket <path/in/bucket>
```

Once it is successfully uploaded, it will print the ALTER SESSION statement
that can be used to activate the script language container in the database.

## How to activate a script language container in the database

If you uploaded a container manually, you can generate the language activation statement with

```bash
exaslct generate-language-activation --flavor-path=flavors/<flavor-name> --bucketfs-name <bucketfs-name> \
                                         --bucket-name <bucket-name> --path-in-bucket <path/in/bucket> --container-name <container-name>
```

where \<container-name> is the name of the uploaded archive without its file extension. To activate the language, execute the generated statement in your database session to activate the container for the current session or system wide.

This command will print a SQL statement to activate the language similar to the following one:

```bash
ALTER SESSION SET SCRIPT_LANGUAGES='<LANGUAGE_ALIAS>=localzmq+protobuf:///<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>?lang=<language>#buckets/<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>/exaudf/exaudfclient[_py3]';
```

## Force a rebuild

Sometimes it is necessary to force a rebuild of a flavor.
A typical reason to update the dependencies is to
fix bugs and security vulnerabilities in the installed dependencies.
To force a rebuild the command line option `--force-rebuild` can be used
with basically all commands of `exaslct`, except the clean commands.

## Partial builds and rebuilds

In some circumstances you want to build or rebuild
only some parts of the flavor. Most likely during development or during CI.
You can specify for a build upper bounds (also called goals)
until which the flavor should be build and for rebuilds
you can define lower bounds from where the rebuild get forced.

You can define upper bounds with the commandline option --goal
for the `exaslct` commands build and push.
The build command only rebuilds the docker images,
but does not export a new container.
All other commands don't support the --goal option,
because they require specific images to be built,
otherwise they would not proceed.

```bash
exaslct build --flavor-path=<path-to-flavor> --goal <build-stage>
```

If you want to build several build-stages at once, you can repeat the `--goal` option.

The following build-stage are currently available:

* udfclient-deps
* language-deps
* build-deps
* build-run
* base-test-deps
* base-test-build-run
* flavor-test-build-run
* flavor-base-deps
* flavor-customization
* release


With the option `--force-rebuild-from`, you can specify from where the rebuild should be forced.
All previous build-stages before this wil use cached versions where possible.
However, if a single stage is built, it will trigger a build for all following build-stages.
The option `--force-rebuild-from` only has an effect together with the option `--force-rebuild`,
without it is ignored.

```bash
exaslct build --flavor-path=<path-to-flavor> --force-rebuild --force-rebuild-from <build-stage>
```

Similar, as for the `--goal` option, you can specify multiple lower bounds
by repeating the `--force-rebuild-from` with different build-stages.

## Using your own remote cache

Exaslct caches images locally and remotely.
For remote caching exaslct can use a docker registry.
The default registry is configured to Docker Hub.
With the command line options `--repository-name`
you can configure your own docker registry as cache.
The `--repository-name` option can be used with all
`exaslct` commands that could trigger a build,
which include build, export, upload and run-db-test commands.
Furthermore, it can be used with the push command which
uploads the build images to the docker registry.
In this case the `--repository-name` option specifies
not only from where to pull cached images during the build,
but also to which cache the built images should be pushed.

You can specify the repository name, as below:

```bash
exaslct export --flavor-path=<path-to-flavor> --repository-name <hostname>[:port]/<user>/<repository-name>
```

## Testing an existing flavor

To test the script language container you can execute the following command:

```bash
exaslct run-db-test --flavor-path=flavors/<flavor-name>
```

**Note: you need docker in privileged mode to execute the tests**

### Testing an existing container file

You can test an existing container file (*.tar.gz) with the following command:

```bash
exaslct run-db-test --flavor-path=flavors/<flavor-name> --use-existing-container <path-to-file>
```

With this additional option, `exaslct` won't build and export the container again, which might be a faster approach if you have access to the container file, but for some reason the internal cache and/or the docker image has been deleted.

**Note**: `exaslct` won't check if the given container file is compatible with the given flavor path. If this is not the case, the tests probably will fail.


## Cleaning up after you are finished

The creation of scripting language container creates or downloads several docker images
which can consume a lot of disk space. Therefore, we recommend removing the Docker images
of a flavor after working with them.

This can be done as follows:

```bash
exaslct clean-flavor-images --flavor-path=flavors/<flavor-name>
```

To remove all images of all flavors you can use:

```bash
exaslct clean-all-images
```

**Please note that this script does not delete the Linux image that is used as basis for the images that were build in the previous steps.
Furthermore, this command doesn't delete cached files in the output directory. The default path for the output directory is .build-output.**
