# Script-Languages-Container-Tool

## Overview

The Script-Languages-Container-Tool (exaslct) is the build tool for the script language container.
You can build, export and upload script-language container from so-called flavors
which are description how to build the script language container. You can find pre-defined flavors
in the [script-languages-release](https://github.com/exasol/script-languages-release) repository.
There we also described how you could customize these flavors to your needs.
<h1 align="center">Exasol Script Languages Container Tool</h1>

<p align="center">
Building script-language container for extending Exasol UDFs.
</p>

<p align="center">

<a href="https://github.com/exasol/script-languages-container-tool/actions/workflows/ci.yml">
    <img src="https://github.com/exasol/script-languages-container-tool/actions/workflows/main.yml/badge.svg?branch=main" alt="Checks Main">
</a>
<a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/pypi/l/exasol-script-languages-container-tool" alt="License">
</a>
<a href="https://pypi.org/project/exasol-script-languages-container-tool/">
    <img src="https://img.shields.io/pypi/dm/exasol-script-languages-container-tool" alt="Downloads">
</a>
<a href="https://pypi.org/project/exasol-script-languages-container-tool/">
    <img src="https://img.shields.io/pypi/pyversions/exasol-script-languages-container-tool" alt="Supported Python Versions">
</a>
<a href="https://pypi.org/project/exasol-script-languages-container-tool/">
    <img src="https://img.shields.io/pypi/v/exasol-script-languages-container-tool" alt="PyPi Package">
</a>
</p>


## In a Nutshell

### Prerequisites

**Note**: Since version 1.0.0 the "starter scripts" shipped with previous version, which pulled the `exaslct` docker container runtime, were removed. If you can't use Python3, you still can use our [AI-lab](https://github.com/exasol/ai-lab) which provides VM images, AMI images and a Docker images, all capable of building script-language-container.

#### For installation

In order to install this tool, your system needs to provide
the following prerequisites:

* Software
    See [Dependencies](doc/dependencies.md)


#### For running

In order to use this tool, your system needs to fulfill the following prerequisites:

* Software
    * Linux
      * Python3 >= 3.10
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

In general, it's good practice to install the package in a virtual environment, using `venv` or `Poetry`.

#### Pip via PyPi

```commandline
python3 -m pip install exasol-script-languages-container-tool
```

#### Pipx via Pypi

If you plan to use `exasol-script-languages-container-tool` on the command line only via the `exaslct` script, we suggest the installation via `pipx`:

```commandline
pipx install exasol-script-languages-container-tool
```


### Usage

For simplicity the following examples use the script version (`exaslct`), which will be installed together with the Python package. The script is just an alias for `python3 -m exasol.slc.tool.main`.

#### How to build an existing flavor?

Create the language container and export it to the local file system

```bash
exaslct export --flavor-path=flavors/<flavor-name> --export-path <export-path>
```

or deploy it directly to the BucketFS (both http and https are supported)

```bash
exaslct deploy --flavor-path=flavors/<flavor-name> --bucketfs-host <hostname-or-ip> --bucketfs-port <port> \
                   --bucketfs-user w --bucketfs-password <password>  --bucketfs-name <bucketfs-name> \
                   --bucket <bucket-name> --path-in-bucket <path/in/bucket> --bucketfs-use-https 1
```

Once it is successfully deployed, it will print the ALTER SESSION statement
that can be used to activate the script language container in the database.

#### How to activate a script language container in the database

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

**Please, refer to the [User Guide](doc/user_guide/user_guide.md) for more detailed information, how to use exalsct.**

## Features

* Build a script language container as docker images
* Export a script language container as an archive which can be used for extending Exasol UDFs
* Upload a script language container as an archive to the Exasol DB's BucketFS
* Generating the activation command for a script language container
* Can use Docker registries, such as Docker Hub, as a cache to avoid rebuilding image without changes
* Can push Docker images to Docker registries
* Run tests for you container against an Exasol DB (docker-db or external db)

## Table of Contents

### Information for Users

* [User Guide](doc/user_guide/user_guide.md)
* [Changelog](doc/changes/changelog.md)

## Information for Developers

* [Developer Guide](doc/developer_guide/developer_guide.md)
* [Dependencies](doc/dependencies.md)
