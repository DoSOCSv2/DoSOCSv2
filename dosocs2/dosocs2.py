#!/usr/bin/env python2

# Copyright (C) 2015 University of Nebraska at Omaha
#
# This file is part of dosocs2.
#
# dosocs2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# dosocs2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dosocs2.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0+

'''Usage:
{0} configtest [-f FILE]
{0} dbinit [-f FILE] [--no-confirm]
{0} generate [-C COMMENT] [-f FILE] [-N NAME] (PACKAGE-ID)
{0} newconfig [-f FILE]
{0} oneshot [-c COMMENT] [-C COMMENT] [-e VER] [-f FILE] [-n NAME] [-N NAME]
    [-r] [-s SCANNERS] [-T FILE] (PATH)
{0} print [-f FILE] [-T FILE] (DOC-ID)
{0} scan [-c COMMENT] [-f FILE] [-n NAME] [-e VER] [-s SCANNERS] [-r] (PATH)
{0} scanproject [--project-file] (PROJECT-FILE)
{0} scanners [-f FILE]
{0} (--help | --version)

Commands:
  configtest    Check configuration
  dbinit        Create tables, views, and initial config file
                  (destructive, will prompt first)
  generate      Generate SPDX document data in the database for a
                  particular package
  newconfig     Create a copy of the default configuration at
                  $XDG_CONFIG_HOME/dosocs2/dosocs2.conf
                  (overwrite existing config)
  oneshot       Scan, generate document, and print document in one
                  command
  print         Render and print a document to standard output
  scan          Scan an archive file or directory
  scanners      List available scanners

Options:
  -C, --doc-comment=COMMENT   Comment for new document (otherwise use empty
                                string)
  -c, --package-comment=COMMENT
                              Comment for new package (otherwise use empty
                                string)
  -e, --package-version=VER   Version string for new package (otherwise use
                                empty string)
  -f, --config=FILE           Alternate config file
  -N, --doc-name=NAME         Name for new document (otherwise create name
                                from package name)
  -n, --package-name=NAME     Name for new package (otherwise create
                                name from filename)
  --project-file              Project Scan option
  -r, --rescan                If any selected scanner already ran on a
                                package/file, run it anyway
  -s, --scanners=SCANNERS     Comma-separated list of scanners to use
                                ('dosocs2 scanners' to see choices)
  -T, --template-file=FILE    Template to use for document generation
  --no-confirm                Don't prompt when dropping/creating tables
                                (dangerous!)

Report bugs to <skorlimarla@unomaha.edu>.
'''

from __future__ import print_function

import os
import pkg_resources
import re
import sys

import docopt

__version__ = '0.16.1'


from . import configtools
from . import dbinit
from . import discover
from . import render
from . import schema as db
from . import spdxdb
from . import util


format_map = {
    'tag': pkg_resources.resource_filename('dosocs2', 'templates/2.0.tag'),
}


def print_hr():
    print('\n' + 79 * '-' + '\n')


def msg(text, **kwargs):
    print('dosocs2' + ': ' + text, **kwargs)
    sys.stdout.flush()


def errmsg(text, **kwargs):
    print('dosocs2' + ': ' + text, file=sys.stderr, **kwargs)
    sys.stdout.flush()


def do_scan(engine, config, package_root, package_file_path=None, selected_scanners=None,
            package_name=None, package_version='', package_comment='', rescan=False):
    if selected_scanners is None:
        selected_scanners = ()
    kwargs = {
        'name': package_name,
        'version': package_version,
        'comment': package_comment,
        'package_root': package_root,
        'package_file_path': package_file_path,
        }
    with engine.begin() as conn:
        package = spdxdb.register_package(conn, **kwargs)
    errmsg('{}: package_id: {}'.format(package_file_path or package_root, package['package_id']))
    for scanner_cls in selected_scanners:
        scanner_kwargs = {
            'package_id': package['package_id'],
            'package_root': package_root,
            'package_file_path': package_file_path,
            'rescan': rescan
            }
        with engine.begin() as conn:
            scanner = scanner_cls(conn, config)
            package_already_done = scanner.package_is_already_done(package['package_id'])
            if not rescan and package_already_done:
                errmsg('{} already ran on package {}'.format(scanner.name, package['package_id']))
            else:
                errmsg('running {} on package {}'.format(scanner.name, package['package_id']))
                scanner.run(**scanner_kwargs)
            if not package_already_done:
                scanner.mark_package_done(package['package_id'])
    return package


def do_configtest(engine, config):
    print_hr()
    print('Config location:')
    if os.path.exists(config.file_location):
        print(config.file_location)
    else:
        print(config.file_location + ' (not present)')
    print_hr()
    print('Effective configuration:\n')
    print('# begin dosocs2 config\n')
    config.dump_to_file(sys.stdout)
    print('\n# end dosocs2 config')
    print_hr()
    print('Testing specified scanner paths...')
    scanner_config_pattern = r'scanner_(.*?)_path'
    for key in sorted(config.config.keys()):
        result = re.match(scanner_config_pattern, key)
        if result:
            print(result.group(1) + ' ({})...'.format(config.config[key]), end='')
            try:
                os.stat(config.config[key])
            except EnvironmentError:
                print('does not exist or is inaccessible.')
            else:
                print('ok.')

    print_hr()
    print('Testing database connection...', end='')
    sys.stdout.flush()
    with engine.begin() as conn:
        conn.execute('select 1;')
    print('ok.')


def main(sysargv=None):
    argv = docopt.docopt(
        doc=__doc__.format(os.path.basename(sys.argv[0])),
        argv=sysargv,
        version=__version__
        )
    alt_config_path = argv['--config']
    doc_id = argv['DOC-ID']
    package_id = argv['PACKAGE-ID']
    package_path = argv['PATH']
    new_doc_comment = argv['--doc-comment'] or ''
    new_doc_name = argv['--doc-name'] or argv['--package-name']
    template_file = argv['--template-file'] or format_map['tag']
    project_file = argv['PROJECT-FILE'] or ''

    # Configuration and scanner discovery
    config = configtools.Config()
    config.make_config_dirs()
    scanners = discover.discover()

    # Pull from alternate config file if specified
    if argv['--config']:
        try:
            # if creating new, don't care if it already exists or not
            if not argv['newconfig']:
                with open(alt_config_path) as _:
                    pass
        except EnvironmentError as ex:
            errmsg('{}: {}'.format(alt_config_path, ex.strerror))
            return 1
        config.file_location = alt_config_path
    config.update_config()

    # Verify existence of selected scanners
    if not argv['--scanners']:
        argv['--scanners'] = config.config['default_scanners']
    selected_scanners = []
    for this_scanner_name in argv['--scanners'].split(','):
        try:
            this_scanner = scanners[this_scanner_name]
        except KeyError:
            errmsg("'{}' is not a known scanner".format(this_scanner_name))
            return 1
        if this_scanner not in selected_scanners:
            selected_scanners.append(this_scanner)

    # Set up connection
    echo = util.bool_from_str(config.config['echo'])
    engine = db.create_connection(config.config['connection_uri'], echo)

    # Now run the indicated command

    if argv['configtest']:
        do_configtest(engine, config)
        return 0

    elif argv['newconfig']:
        try:
            configresult = config.create_local_config()
        except EnvironmentError as e:
            errmsg('failed to write config file to {}: {}'.format(config.file_location, e.strerror))
            return 1
        else:
            msg('wrote config file to {}'.format(config.file_location))
            return 0

    elif argv['scanners']:
        default_scanners = config.config['default_scanners'].split(',')
        for s in sorted(scanners):
            if s in default_scanners:
                print(s + ' [default]')
            else:
                print(s)
        return 0

    elif argv['dbinit']:
        errmsg('preparing to initialize the database ({})'.format(str(engine)[7:-1]))
        errmsg('all existing data will be deleted!')
        errmsg('type the word "YES" (all uppercase) to commit.')
        if not argv['--no-confirm']:
            answer = raw_input()
            if answer != 'YES':
                errmsg('canceling operation.')
                return 1
        else:
            print('YES')
        return 0 if dbinit.initialize(engine, db, __version__) else 1

    elif argv['print']:
        with engine.begin() as conn:
            if spdxdb.fetch(conn, db.documents, doc_id) is None:
                errmsg('document id {} not found in the database.'.format(doc_id))
                return 1
            print(render.render_document(conn, doc_id, template_file))

    elif argv['generate']:
        kwargs = {
            'name': new_doc_name,
            'comment': new_doc_comment,
            'prefix': config.config['namespace_prefix']
            }
        with engine.begin() as conn:
            package = spdxdb.fetch(conn, db.packages, package_id)
            if package is None:
                errmsg('package id {} not found in the database.'.format(package_id))
                return 1
            document_id = spdxdb.create_document(conn, package=package, **kwargs)['document_id']
        fmt = '(package_id {}): document_id: {}\n'
        sys.stderr.write(fmt.format(package_id, document_id))

    elif argv['scan']:
        kwargs = {
            'config': config.config,
            'engine': engine,
            'selected_scanners': selected_scanners,
            'package_name': argv['--package-name'],
            'package_version': argv['--package-version'],
            'package_comment': argv['--package-comment'],
            'rescan': argv['--rescan']
            }
        if os.path.isfile(package_path):
            with util.tempextract(package_path) as (tempdir, _):
                kwargs['package_root'] = tempdir
                kwargs['package_file_path'] = package_path
                do_scan(**kwargs)
        else:
            os.stat(package_path)  # force exception if nonexisstent
            kwargs['package_root'] = package_path
            kwargs['package_file_path'] = None
            do_scan(**kwargs)
    elif argv['scanproject']:
         use_info = '[-] Contact DoSOCSv2 Organization for project level info'
         print("{0} {1}".format(use_info, os.path.abspath(project_file)))

    elif argv['oneshot']:
        kwargs = {
            'config': config.config,
            'engine': engine,
            'selected_scanners': selected_scanners,
            'package_name': argv['--package-name'],
            'package_version': argv['--package-version'],
            'package_comment': argv['--package-comment'],
            'rescan': argv['--rescan']
            }
        if os.path.isfile(package_path):
            with util.tempextract(package_path) as (tempdir, _):
                kwargs['package_root'] = tempdir
                kwargs['package_file_path'] = package_path
                package = do_scan(**kwargs)
        else:
            os.stat(package_path)  # force exception if nonexisstent
            kwargs['package_root'] = package_path
            kwargs['package_file_path'] = None
            package = do_scan(**kwargs)
        with engine.begin() as conn:
            document = spdxdb.get_doc_by_package_id(conn, package_id)
            if document:
                doc_id = document['document_id']
            else:
                kwargs = {
                    'name': new_doc_name,
                    'comment': new_doc_comment,
                    'prefix': config.config['namespace_prefix']
                    }
                doc_id = spdxdb.create_document(conn, package=package, **kwargs)['document_id']
            fmt = '{}: document_id: {}\n'
            sys.stderr.write(fmt.format(package_path, doc_id))
        with engine.begin() as conn:
            print(render.render_document(conn, doc_id, template_file))
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
