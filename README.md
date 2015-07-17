dosocs2
=======

dosocs2 is a command-line app for managing SPDX 2.0 documents and data. It can
scan software packages (e.g. tarballs) to produce SPDX information, store that
information in a relational database, and extract it in tag-value format
on request.

[SPDX](http://www.spdx.org) is a standard format for communicating information
about the licenses and copyrights associated with a software package. dosocs2
makes use of the SPDX 2.0 standard, released in May 2015.

dosocs2 is currently (July 2015) under heavy development; it should be
considered experimental, not production-ready, and subject to frequent
backwards-incompatible changes until a proper release.

### Current deviations from SPDX 2.0 specification

* Exactly one package per document is required. (SPDX 2.0 allows zero or more
  packages per document.)
* Files in a document can only exist within a package. (SPDX 2.0 allows files
  to exist outside of a package.)
* Checksums are always assumed to be SHA-1. (SPDX 2.0 permits SHA-1, SHA-256,
  and MD5)
* A file may be an artifact of only one project.
* License expression syntax is not supported.
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
- PostgreSQL 8.x or later version (can be on a separate machine)
- <a href="http://www.fossology.org/">FOSSology</a> 2.5.x or later version

### Python libraries

- [docopt](http://docopt.org/)
- [Jinja2](http://jinja.pocoo.org/)
- [psycopg2](http://initd.org/psycopg/)
- [python-magic](https://github.com/ahupp/python-magic)
- [SQLAlchemy](http://www.sqlalchemy.org/)

All Python dependencies are handled by the setup script.


Installation
------------

First off, I recommend installing and running `dosocs2` inside a Python
[virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/), but it
is in no way a requirement.

Grab the latest release--or, if you are feeling adventurous, clone the
repository--and use `pip` to install it as a package. If you are not inside a
virtualenv you may have to run `pip` as root.

    $ pip install ./dosocs2

You will have to create the `spdx` (or whatever you want to call it) role and
database yourself (although I recommend setting a different password than the
one given...):

    postgres=# create role spdx with login password 'spdx';
    postgres=# create database spdx with owner spdx;


Generate an initial config file:

    $ dosocs2 newconfig
    dosocs2: wrote config file to /home/tgurney/.config/dosocs2/dosocs2.conf

Then open up the config file and make sure you are pointed to the correct
PostgreSQL server, with a valid username/password. You also need to set the
path of the default `nomos` scanner (part of FOSSology) if it is not already
correct.

Finally, to create all necessary tables and views in the database:

    $ dosocs2 dbinit


Usage
-----

The simplest use case is scanning a package, generating a
document, and printing the document in one shot:

    $ dosocs2 oneshot package.tar.gz
    document_id: 1
    package_id: 1
    [... document output here ...]

Also works on directories:

    $ dosocs2 oneshot ./path/to/directory

The scan results and other collected metadata are saved in the database
so that subsequent document generations will be much faster.

To scan a package and store its information in the database:

    $ dosocs2 scan package.tar.gz
    package_id: 456

No document has been created yet. To create one in the database (specifying the
package ID):

    $ dosocs2 generate 456
    document_id: 123

Then, to compile and output the document in tag-value format:

    $ dosocs2 print 123
    [... document output here ...]


History
-------

dosocs2 owes its name and concept to the
[DoSOCS](https://github.com/socs-dev-env/DoSOCS) tool created by Zach
McFarland, which in turn was spun off from the `do_spdx` plugin for Yocto
Project, created by Jake Cloyd and Liang Cao.

dosocs2 aims to fill the same role as DoSOCS, but with support for SPDX 2.x, a
larger feature set, and a more modular implementation, among other changes.


Maintainers
-----------

[Thomas T. Gurney](https://github.com/ttgurney)
