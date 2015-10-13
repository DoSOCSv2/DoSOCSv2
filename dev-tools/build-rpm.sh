#!/bin/bash
python2 setup.py bdist_rpm --python python2 --group "Development/Tools" --vendor "Thomas T Gurney <tgurney@unomaha.edu>" --requires gcc,git,make,postgresql-devel,glib2-devel,sqlite,python-sqlalchemy,python-jinja2,python-magic,python-psycopg2 --post-install scripts/install-nomos.sh
