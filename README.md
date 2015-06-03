dosocs2
=======

dosocs2 is a command-line app for managing SPDX 2.0 documents and data. It can
scan software packages (e.g. tarballs) to produce SPDX information, store that
information in a relational database, and extract it in RDF or tag-value format
on request.

[SPDX](http://www.spdx.org) is a standard format for communicating information
about the licenses and copyrights associated with a software package. dosocs2
makes use of the SPDX 2.0 standard, released in May 2015.

dosocs2 is currently (June 2015) under heavy development; it should be
considered experimental, not production-ready, and subject to frequent
backwards-incompatible changes until a proper release.


License and Copyright
---------------------
dosocs2 is copyright © 2014-2015 University of Nebraska at Omaha and other
contributors.

The dosocs2 code is licensed under the terms of the Apache License 2.0
(see LICENSE). All associated documentation is licensed under the terms of the
Creative Commons Attribution Share-Alike 3.0 license (see CC-BY-SA-3.0).


Dependencies
------------
- Python 2.7
- PostgreSQL
- <a href="http://www.fossology.org/">FOSSology</a>

Python libraries
~~~~~~~~~~~~~~~~
- [docopt](http://docopt.org/)
- [Jinja2](http://jinja.pocoo.org/)
- [psycopg2](http://initd.org/psycopg/)
- [python-magic](https://github.com/ahupp/python-magic)
- [SQLSoup](https://sqlsoup.readthedocs.org/en/latest/)

You can install all of these in one shot with the included `requirements.txt`
file:

    $ pip install -r requirements.txt


Installation
------------
On my todo list!


Maintainers
-----------
[Thomas T. Gurney](https://github.com/ttgurney)
