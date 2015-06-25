#!/usr/bin/env python2

# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2014-2015 University of Nebraska at Omaha (UNO) and other
# contributors.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Usage:
{0} generate [-c FILE] (PACKAGE-ID)
{0} dbinit [-c FILE] [--no-confirm]
{0} newconfig
{0} oneshot [-c FILE] [-p NAME] [-s SCANNER] (PATH)
{0} print [-c FILE] (DOC-ID)
{0} scan [-n] [-c FILE] [-p NAME] [-s SCANNER] (PATH)
{0} scanners [-c FILE]
{0} (--help | --version)

Commands:
  generate      Generate SPDX document data in the database for a
                  particular package
  dbinit        Create tables, views, and initial config file
                  (destructive, will prompt first)
  newconfig     Create a copy of the default configuration at
                  $XDG_CONFIG_HOME/dosocs2/dosocs2.conf
                  (overwrite existing config)
  oneshot       Scan, generate document, and print document in one
                  command
  print         Render and print a document to standard output
  scan          Scan an archive file or directory
  scanners      List available scanners

General options:
  -c, --config=FILE           Alternate config file

Options for 'init':
      --no-confirm            Don't prompt first

Options for 'scan', 'oneshot':
  -p, --package-name=NAME     Specify name for new package (otherwise
                                create name from filename)
  -s, --scanner=SCANNER       Specify scanner to use
                                ('dosocs2 scanners' to see choices)

Report bugs to <tgurney@unomaha.edu>.
'''

from __future__ import print_function

import os
import pkg_resources
import sys

import docopt
import sqlsoup

from .spdxdb import Transaction
from . import config
from . import dbinit
from . import render
from . import scanners

__version__ = '0.1.0'

format_map = {
    'tag': pkg_resources.resource_filename('dosocs2', 'templates/2.0.tag'),
}


def msg(text, **kwargs):
    print('dosocs2' + ': ' + text, **kwargs)
    sys.stdout.flush()


def errmsg(text, **kwargs):
    print('dosocs2' + ': ' + text, file=sys.stderr, **kwargs)
    sys.stdout.flush()


def initialize(db):
    url = 'http://spdx.org/licenses/'
    msg('dropping all views...', end='')
    result = dbinit.drop_all_views(db)
    print('ok.')
    msg('dropping all tables...', end='')
    result = dbinit.drop_all_tables(db)
    print('ok.')
    msg('creating all tables...', end='')
    result = dbinit.create_all_tables(db)
    print('ok.')
    msg('committing changes...', end='')
    db.commit()
    print('ok.')
    msg('creating all views...', end='')
    result = dbinit.create_all_views(db)
    print('ok.')
    msg('loading licenses...', end='')
    result = dbinit.load_licenses(db, url)
    if not result:
        errmsg('error!')
        errmsg('failed to download and load the license list')
        errmsg('check your connection to ' + url + ' and make sure it is the correct page')
        return False
    else:
        print('ok.')
    msg('loading creator types...', end='')
    dbinit.load_creator_types(db)
    print('ok.')
    msg('loading default creator...', end='')
    dbinit.load_default_creator(db, 'dosocs2-' + __version__)
    print('ok.')
    msg('loading annotation types...', end='')
    dbinit.load_annotation_types(db)
    print('ok.')
    msg('loading file types...', end='')
    dbinit.load_file_types(db)
    print('ok.')
    msg('loading relationship types...', end='')
    dbinit.load_relationship_types(db)
    print('ok.')
    msg('committing changes...', end='')
    db.commit()
    print('ok.')
    return True


def main():
    argv = docopt.docopt(doc=__doc__.format(os.path.basename(sys.argv[0])), version=__version__)
    doc_id = argv['DOC-ID']
    document = None
    db = sqlsoup.SQLSoup(config.connection_uri)
    package_id = argv['PACKAGE-ID']
    package_path = argv['PATH']
    output_format = 'tag'
    alt_name = argv['--package-name']
    this_scanner = argv['--scanner'] or config.config['dosocs2']['default_scanner']
    if this_scanner not in scanners.scanners:
        errmsg("'{}' is not a known scanner".format(this_scanner))
        sys.exit(1)

    if argv['--config']:
        config.update_config(argv['--config'])

    if argv['newconfig']:
        config_path = config.DOSOCS2_CONFIG_PATH
        configresult = config.create_user_config()
        if not configresult:
            errmsg('failed to write config file to {}'.format(config_path))
        else:
            msg('wrote config file to {}'.format(config_path))
        sys.exit(0 if configresult else 1)

    elif argv['scanners']:
        for s in sorted(scanners.scanners):
            if config.config['dosocs2']['default_scanner'] == s:
                print(s + ' [default]')
            else:
                print(s)
        sys.exit(0)

    elif argv['dbinit']:
        if not argv['--no-confirm']:
            errmsg('preparing to initialize the database')
            errmsg('all existing data will be deleted!')
            errmsg('make sure you are connected to the internet before continuing.')
            errmsg('type the word "YES" (all uppercase) to commit.')
            answer = raw_input()
            if answer != 'YES':
                errmsg('canceling operation.')
                sys.exit(1)
        sys.exit(0 if initialize(db) else 1)

    elif argv['print']:
        with Transaction(db) as t:
            document = t.fetch('documents', doc_id)
        if document is None:
            errmsg('document id {} not found in the database.'.format(doc_id))
            sys.exit(1)
        print(render.render_document(db, doc_id, format_map[output_format]))

    elif argv['generate']:
        with Transaction(db) as t:
            package = t.fetch('packages', package_id)
            if package is None:
                errmsg('package id {} not found in the database.'.format(package_id))
                sys.exit(1)
            document = t.create_document(package_id)
            print('(package_id {}): document_id: {}'.format(package_id, document.document_id))

    elif argv['scan']:
        with Transaction(db) as t:
            package = t.scan_package(package_path, this_scanner, alt_name)
        print('{}: package_id: {}'.format(package_path, package.package_id))

    elif argv['oneshot']:
        with Transaction(db) as t:
            package = t.scan_package(package_path, this_scanner, alt_name)
            package_id = package.package_id
            sys.stderr.write('{}: package_id: {}\n'.format(package_path, package_id))
        with Transaction(db) as t:
            document = (
                db.documents
                .filter(db.documents.package_id == package_id)
                .first()
                )
            if document:
                doc_id = document.document_id
            else:
                document = t.create_document(package_id)
                doc_id = document.document_id
            sys.stderr.write('{}: document_id: {}\n'.format(package_path, doc_id))
        print(render.render_document(db, doc_id, format_map[output_format]))



if __name__ == "__main__":
    main()
