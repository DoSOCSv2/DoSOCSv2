dosocs2
=======

dosocs2 is a command-line tool for managing SPDX 2.0 documents and data. It can
scan source code distributions to produce SPDX information, store that
information in a relational database, and extract it in a plain-text format
on request.

dosocs2 enables easy creation of a "bill of materials" for any software package,
and can even be used in the creation and continuous maintenance of an inventory
of all open-source software used in an organization.

[SPDX](http://www.spdx.org) is a standard format for communicating information
about the contents of a software package, including license and copyright
information. dosocs2 supports the SPDX 2.0 standard, released in May 2015.

dosocs2 is under heavy development; expect frequent backwards-incompatible
changes until a 1.x.x release!

### Current deviations from SPDX 2.0 specification

* Exactly one package per document is required. (SPDX 2.0 allows zero or more
  packages per document.)
* Files in a document can only exist within a package. (SPDX 2.0 allows files
  to exist outside of a package.)
* Checksums are always assumed to be SHA-1. (SPDX 2.0 permits SHA-1, SHA-256,
  and MD5)
* A file may be an artifact of only one project.
* License expression syntax is not parsed; license expressions are interpreted as license
  names that are not on the SPDX license list.
* Deprecated fields from SPDX 1.2 (reviewer info and file dependencies) are not supported.


License and Copyright
---------------------

dosocs2 is copyright © 2014-2015 University of Nebraska at Omaha and other
contributors.

The dosocs2 code is licensed under the terms of the Apache License 2.0
(see LICENSE). All associated documentation is licensed under the terms of the
Creative Commons Attribution Share-Alike 3.0 license (see CC-BY-SA-3.0).


Dependencies
------------

- Python 2.7.x

Optional:
- [FOSSology](http://www.fossology.org/) 2.5.x or later version (for
  license identification)
- [OWASP dependency-check](https://github.com/jeremylong/DependencyCheck)
  (for vulnerability identification)
- PostgreSQL 8.x or later version (can be on a separate machine)

Python libraries:
- All Python dependencies are handled automatically by `pip`.


Installation
------------

First off, I recommend installing and running `dosocs2` inside a Python
[virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/), but it
is not a requirement.

### Step 1 - Download and install

[Grab the latest release](https://github.com/ttgurney/dosocs2/releases)
and use `pip` to install it as a package. If you are not inside a virtualenv
you may have to run `pip` as root (not recommended!). Replace `0.x.x` with
the latest release version number.

    $ tar xf 0.x.x.tar.gz
    $ pip install ./dosocs2-0.x.x

Or, if you want PostgreSQL support to go along with the standard SQLite support:

    $ tar xf 0.x.x.tar.gz
    $ pip install ./dosocs2-0.x.x[postgres]


### Step 2 - Change the default configuration

Not required, but strongly recommended, is to generate an initial config
file:

    $ dosocs2 newconfig
    dosocs2: wrote config file to /home/tom/.config/dosocs2/dosocs2.conf

The default config points to a SQLite database stored in your home directory.
For example, for user `tom`, this database would be created at
`/home/tom/.config/dosocs2/dosocs2.sqlite3`. If you like, you can open the
config file and change the `connection_uri` variable to use a different
location for the database.

If you have [FOSSology](http://www.fossology.org/) installed, you also need
to set the path of the default `nomos` scanner if it is not already correct.
Likewise for any of the other supported scanners you want to use
(see [doc/scanners.md](doc/scanners.md))


### Step 3 (Optional) - Add PostgreSQL configuration

Follow this step if you want to use PostgreSQL instead of SQLite for the
SPDX database.

You will have to create the `spdx` (or whatever name you want) role and
database yourself.  I recommend setting a different password than the
one given...:

    $ sudo -u postgres psql
    psql (9.3.9)
    Type "help" for help.

    postgres=# create role spdx with login password 'spdx';
    CREATE ROLE
    postgres=# create database spdx with owner spdx;
    CREATE DATABASE

Then change the `connection_uri` variable in your `dosocs2.conf`:

    # connection_uri = postgresql://user:pass@host:port/database
    connection_uri = postgresql://spdx:spdx@localhost:5432/spdx


### Step 4 - Database setup

Finally, to create all necessary tables and views in the database:

    $ dosocs2 dbinit

You only need to do this once. **This command will drop all
existing tables from your SPDX database, so be careful!**

Usage
-----

The simplest use case is scanning a package, generating a
document, and printing an SPDX document in one shot:

    $ dosocs2 oneshot package.tar.gz
    dosocs2: package.tar.gz: package_id: 1
    dosocs2: running nomos on package 1
    dosocs2: package.tar.gz: document_id: 1
    [... document output here ...]

Also works on directories:

    $ dosocs2 oneshot ./path/to/directory

The scan results and other collected metadata are saved in the database
so that subsequent document generations will be much faster.

To just scan a package and store its information in the database:

    $ dosocs2 scan package.tar.gz
    dosocs2: package_tar_gz: package_id: 456
    dosocs2: running nomos on package 456

In the default configuration, if a scanner is not specified, only `nomos`
is run by default. It gathers license information, but is a bit slow.
One can use the `-s` option to explicitly specify which scanners to run:

    $ dosocs2 scan -s nomos_deep,dependency_check package.tar.gz
    dosocs2: package_tar_gz: package_id: 456
    dosocs2: running nomos_deep on package 456
    dosocs2: running dependency_check on package 456

After `dosocs2 scan`, no SPDX document has yet been created.
To create one in the database (specifying the package ID):

    $ dosocs2 generate 456
    dosocs2: (package_id 456): document_id: 123

Then, to compile and output the document in tag-value format:

    $ dosocs2 print 123
    [... document output here ...]

Use `dosocs2 --help` to get the full help text. The `doc` directory
here also provides more detailed information about how `dosocs2` works
and how to use it.


History
-------

dosocs2 owes its name and concept to the
[DoSOCS](https://github.com/socs-dev-env/DoSOCS) tool created by Zac
McFarland, which in turn was spun off from the `do_spdx` plugin for Yocto
Project, created by Jake Cloyd and Liang Cao.

dosocs2 aims to fill the same role as DoSOCS, but with support for SPDX 2.x, a
larger feature set, and a more modular implementation, among other changes.


Maintainers
-----------

[Thomas T. Gurney](https://github.com/ttgurney)
