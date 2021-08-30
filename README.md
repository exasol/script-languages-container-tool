# Script-Languages-Container-Tool

## Overview

The Script-Languages-Container-Tool (exaslct) is the build tool for the script language container.
You can build, export and upload script-language container from so-called flavors 
which are description how to build the script language container. You can find pre-defined flavors 
in the [script-languages-release](https://github.com/exasol/script-languages-release) repository. 
There we also described how you could customize these flavors to your needs.

## In a Nutshell

### Prerequisites

#### For installation

In order to install this tool, your system needs to provide 
the following prerequisites:

* Software
    * Linux
      * [bash](https://www.gnu.org/software/bash/) >= 4.2
    * MacOsX
      * [bash](https://www.gnu.org/software/bash/) > 3.2
    * [coreutils](https://www.gnu.org/software/coreutils/)
      * sha512sum
      * sed
    * [curl](https://curl.se/)


#### For running

In order to use this tool, your system needs to fulfill the following prerequisites:

* Software
    * Linux
      * [bash](https://www.gnu.org/software/bash/) >= 4.2
      * [coreutils](https://www.gnu.org/software/coreutils/)
        * readlink with -f option
        * realpath  
        * dirname
    * MacOsX (Please see limitations on [MacOsX](#macosx-limitations))
      * [bash](https://www.gnu.org/software/bash/) >= 3.2
      * [coreutils](https://www.gnu.org/software/coreutils/)
        * greadlink with -f option
        * realpath  
        * dirname
    * [Docker](https://docs.docker.com/) >= 17.05 
      * with support for [multi-stage builds required](https://docs.docker.com/develop/develop-images/multistage-build/)
      * host volume mounts need to be allowed
    
* System Setup  
    * We recommend at least 50 GB free disk space on the partition 
      where Docker stores its images, on linux Docker typically stores 
      the images at /var/lib/docker.
    * For the partition where the output directory (default: ./.build_output)
      is located we recommend additionally at least 10 GB free disk space.

Further, prerequisites might be necessary for specific tasks. These are listed under the corresponding section.

### Installation

Download the installation and update script via:

```
curl -L -o install_or_update_exaslct.sh https://raw.githubusercontent.com/exasol/script-languages-container-tool/main/installer/install_or_update_exaslct.sh
```

Before you continue with installation, please compute with the following command 
the sha512 hash sum of the downloaded file and compare it with its 
[checksum file](installer/checksums/install_or_update_exaslct.sh.sha512sum):

```
sha512sum install_or_update_exaslct.sh
```

If the checksums are identical, you can continue with the installation. 
Per default, the script installs exaslct into the current working directory.
It creates a script directory `exaslct_scripts` and the symlink `exaslct`
to the starter script. If you want to change the path to the script directory 
you can set the environment variable `EXASLCT_INSTALL_DIRECTORY` and 
if you want to create the symlink somewhere else you can set `EXASLCT_SYM_LINK_PATH`.  

```
bash install_or_update_exaslct.sh [version|git-commit-id|branch|tag] 
```

You can use the same script to change the version of your current installation.
You only need to provide a different version, git-commit-id, branch or tag. 

### Usage

#### How to build an existing flavor?

Create the language container and export it to the local file system

```bash
./exaslct export --flavor-path=flavors/<flavor-name> --export-path <export-path>
```

or upload it directly into the BucketFS (currently http only, https follows soon)

```bash
./exaslct upload --flavor-path=flavors/<flavor-name> --database-host <hostname-or-ip> --bucketfs-port <port> \ 
                   --bucketfs-username w --bucketfs-password <password>  --bucketfs-name <bucketfs-name> \
                   --bucket-name <bucket-name> --path-in-bucket <path/in/bucket>
```

Once it is successfully uploaded, it will print the ALTER SESSION statement
that can be used to activate the script language container in the database.

#### How to activate a script language container in the database

If you uploaded a container manually, you can generate the language activation statement with

```bash
./exaslct generate-language-activation --flavor-path=flavors/<flavor-name> --bucketfs-name <bucketfs-name> \
                                         --bucket-name <bucket-name> --path-in-bucket <path/in/bucket> --container-name <container-name>
```

where \<container-name> is the name of the uploaded archive without its file extension. To activate the language, execute the generated statement in your database session to activate the container for the current session or system wide.

This command will print a SQL statement to activate the language similar to the following one:

```bash
ALTER SESSION SET SCRIPT_LANGUAGES='<LANGUAGE_ALIAS>=localzmq+protobuf:///<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>?lang=<language>#buckets/<bucketfs-name>/<bucket-name>/<path-in-bucket>/<container-name>/exaudf/exaudfclient[_py3]';
```

**Please, refer to the User Guide for more detailed information, how to use exalsct.**

## Features

* Build a script language container as docker images
* Export a script language container as an archive which can be used for extending Exasol UDFs
* Upload a script language container as an archive to the Exasol DB's BucketFS
* Generating the activation command for a script language container
* Can use Docker registries, such as Docker Hub, as a cache to avoid rebuilding image without changes
* Can push Docker images to Docker registries
* Run tests for you container against an Exasol DB (docker-db or external db)

## Limitations

* Caution with symbolic links: 
  If you use symbolic links inside any directory of the command line arguments
  they must not point to files or directories outside the root of the path of the 
  command line argument (i.e. --flavor-path ./flavors/my_flavor/ => There must be no symbolic
  link inside ./flavors/my_flavor point to anywhere outside of ./flavors/my_flavor).
  Background: Local directories paths must be mounted manually to the docker container. 
  We currently support only the mounting of the given command line arguments, but we do not analyze
  the content of those directories.
  Plan is to fix this limitation with [#35](https://github.com/exasol/script-languages-container-tool/issues/35)

### MacOsX Limitations
  
* On MacOsX all arguments (flavors path, output directory, etc.) must point to locations within the current directory (background is that the MacOsX version does not support mount binding additional directories).

## Table of Contents

### Information for Users

* [User Guide](doc/user_guide/user_guide.md)
* [Changelog](doc/changes/changelog.md)

## Information for Developers

* [Developer Guide](doc/developer_guide/developer_guide.md)
* [Dependencies](doc/dependencies.md)
