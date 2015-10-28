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

"""Interfaces to external scanning tools.

Includes the Scanner base class, the WorkItem class, and some predefined
Scanner subclasses.
"""

import os
import re
import subprocess
from collections import namedtuple

from sqlalchemy import select, and_
import xmltodict

from . import util
from . import scanresult
from . import schema as db
from . import spdxdb
from . import config


"""A file (already registered) to be processed by a scanner."""
WorkItem = namedtuple('WorkItem', ['file_id', 'path'])


class Scanner(object):

    """Base class for connectors to external scanning tools.

    Any new connectors should inherit from Scanner or one of its subclasses,
    and at least override process_file(), store_results(), and the 'name'
    property.

    Instantiating the base Scanner class provides a 'dummy' scanner,
    in which the process_file() and store_results() methods are no-ops. The
    'dummy' scanner is otherwise a well-behaved scanner, and no other methods
    strictly need to be overridden by subclasses.
    """

    """Name for this scanner, used in all contexts (including the database).

    All scanner names must be unique, thus subclasses must override this
    property. Not doing so will lead to strange results.
    """
    name = 'dummy'

    def __init__(self, conn):
        """Initialize Scanner object.

        Register the scanner in the database if it is not already registered.
        Other initialization (such as reading certain variables from
        the dosocs2 config file) may be done here by subclasses.
        """
        self.conn = conn
        self.register()

    def get_file_list(self, package_id, package_root):
        """Return list of WorkItems for all files in a specified package.

        Arguments:
        package_id -- ID of package (must already be registered in DB)
        package_root -- Path to the root of the package; must be a directory
        """
        query = (
            select([
                db.packages_files.c.file_id,
                db.packages_files.c.file_name
                ])
            .where(db.packages_files.c.package_id == package_id)
            )
        file_list = []
        for row in self.conn.execute(query):
            kwargs = {
                'path': os.path.join(package_root, row['file_name'][2:]),
                'file_id': row['file_id']
                }
            file_list.append(WorkItem(**kwargs))
        return file_list

    def run(self, package_id, package_root, package_file_path=None, rescan=False):
        """Scan the specified package, skipping already-scanned files.

        Return None.

        Arguments:
        package_id -- ID of package (must already be registered in DB)
        package_root -- Path to the root of the package; must be a directory.
          In the case of a package that is an archive (like a .tar.gz), this
          would be the path to the root of the unpacked directory structure.
        package_file_path -- If the package exists also as a single file
          (.tar.gz, .jar, whatever), this is the path to that file. Otherwise
          the package is treated as a directory tree with no corresponding
          archive file.
        rescan -- Boolean. If True, scan all files regardless of whether or
          not this scanner has already scanned them. Subclasses may choose
          to ignore this parameter, and always rescan regardless of
          already-scanned status.

        In the default implementation, this method does these things:
        1. Get the file list based on the specified package ID and
          package root path (self.get_file_list())
        2. Invoke self.process_file() on each file that has not already been
          scanned (determined by self.file_is_already_done())
        3. Store the scan results (with self.store_results())
        4. Mark all files that were scanned in this run as done
          (self.mark_files_done())
        """
        all_files = self.get_file_list(package_id, package_root)
        processed_files = {}
        files_to_mark = set()
        for file in all_files:
            already_done = self.file_is_already_done(file)
            if rescan or not already_done:
                processed_files[file] = self.process_file(file)
            if not already_done:
                files_to_mark.add(file)
        self.store_results(processed_files)
        self.mark_files_done(files_to_mark)

    def process_file(self, file):
        """Invoke an actual scan on a single file. Return the scan result.

        Arguments:
        file -- WorkItem object.

        The nature of the returned scan result object will depend on which
        scanner is being called (and what type of results are expected by
        self.store_results())

        In the base Scanner class, this method returns None, so it must be
        overridden in a subclass.

        """
        pass

    def store_results(self, processed_files):
        """Store scan results in the database. Return None.

        Arguments:
        processed_files -- A mapping (dictionary) of WorkItems to scan result
          objects.  The nature of these scan result objects depends on which
          scanner is being called.

        In the base Scanner class, this method does nothing, so it must be
        overridden in a subclass.
        """
        pass

    def register(self):
        """Register scanner in the database if not already registered.

        Also set self.pk equal to the primary key of the record in the scanners
        table corresponding to this scanner.

        Return None.
        """
        if getattr(self, 'pk', None) is not None:
            return
        query = (
            select([db.scanners])
            .where(db.scanners.c.name == self.name)
            )
        [found_scanner] = self.conn.execute(query).fetchall() or [None]
        if found_scanner is not None:
            self.pk = found_scanner['scanner_id']
        else:
            self.pk = spdxdb.insert(self.conn, db.scanners, {'name': self.name})

    def file_is_already_done(self, file):
        """Return True if scanner has already scanned this file.

        Return False otherwise.
        """
        query = (
            select([db.files_scans])
            .where(
                and_(
                    db.files_scans.c.file_id == file.file_id,
                    db.files_scans.c.scanner_id == self.pk
                    )
                )
            )
        [result] = self.conn.execute(query).fetchall() or [None]
        return (result is not None)

    def package_is_already_done(self, package_id):
        """Return True if scanner has already scanned this package.

        Return False otherwise.
        """
        query = (
            select([db.packages_scans])
            .where(
                and_(
                    db.packages_scans.c.package_id == package_id,
                    db.packages_scans.c.scanner_id == self.pk
                    )
                )
            )
        [result] = self.conn.execute(query).fetchall() or [None]
        return (result is not None)

    def mark_files_done(self, files):
        """Create rows in the database to mark files as scanned. Return None.

        Arguments:
        files -- List of WorkItems corresponding to the files to be marked.
          Duplicates are OK, however, rows in the files_scans table for these
          items must not already exist, otherwise this method will fail by
          attempting to violate a unique constraint in the database.
        """
        rows = []
        file_ids_seen = set()
        for file in files:
            if file.file_id in file_ids_seen:
                continue
            file_scan_params = {
                'file_id': file.file_id,
                'scanner_id': self.pk,
                }
            rows.append(file_scan_params)
            file_ids_seen.add(file.file_id)
        spdxdb.bulk_insert(self.conn, db.files_scans, rows)

    def mark_package_done(self, package_id):
        package_scan_params = {
            'package_id': package_id,
            'scanner_id': self.pk,
            }
        spdxdb.insert(self.conn, db.packages_scans, package_scan_params)


class FileLicenseScanner(Scanner):

    """Scanner subclass that implements store_results() for those scanners
    whose result is a list of license short names.

    New connectors to external license scanners should probably inherit from
    this and not from Scanner.
    """

    def store_results(self, processed_files):
        licenses_to_add = []
        for (file, license_names) in processed_files.iteritems():
            licenses = []
            for license_name in license_names:
                license_kwargs = {
                    'conn': self.conn,
                    'short_name': license_name,
                    'comment': 'found by ' + self.name
                    }
                lic = scanresult.lookup_or_add_license(**license_kwargs)
                licenses.append(lic)
            for license in licenses:
                file_license_kwargs = {
                    'file_id': file.file_id,
                    'license_id': license['license_id'],
                    'extracted_text': ''
                    }
                licenses_to_add.append(file_license_kwargs)
        scanresult.add_file_licenses(self.conn, licenses_to_add)


class Monk(FileLicenseScanner):

    """Connector to FOSSology's 'monk' license scanner."""

    name = 'monk'

    def __init__(self, conn):
        super(Monk, self).__init__(conn)
        self.exec_path = config.config['scanner_' + self.name + '_path']
        self.search_pattern = re.compile('found diff match between \"(.*?)\" and \"(.*?)\"')

    def process_file(self, file):
        args = (self.exec_path, file.path)
        output = subprocess.check_output(args)
        scan_result = set()
        for line in output.split('\n'):
            m = re.match(self.search_pattern, line)
            if m is None:
                continue
            scan_result.update({
                lic_name
                for lic_name in m.group(2).split(',')
                })
        return scan_result


class Nomos(FileLicenseScanner):

    """Connector to FOSSology's 'nomos' license scanner."""

    name = 'nomos'

    def __init__(self, conn):
        super(Nomos, self).__init__(conn)
        self.exec_path = config.config['scanner_' + Nomos.name + '_path']
        self.search_pattern = re.compile(r'File (.+?) contains license\(s\) (.+)')

    def process_file(self, file):
        args = (self.exec_path, '-l', file.path)
        output = subprocess.check_output(args)
        scan_result = set()
        for line in output.split('\n'):
            m = re.match(self.search_pattern, line)
            if m is None:
                continue
            scan_result.update({
                lic_name
                for lic_name in m.group(2).split(',')
                if lic_name != 'No_license_found'
                })
        return scan_result


class Copyright(Scanner):

    """Connector to FOSSology's 'copyright' scanner."""

    name = 'copyright'

    def __init__(self, conn):
        super(Copyright, self).__init__(conn)
        self.exec_path = config.config['scanner_' + self.name + '_path']
        self.search_pattern = re.compile(r"\t\[[0-9]+:[0-9]+:statement\] ['](.*?)[']", re.DOTALL)

    def process_file(self, file):
        args = (self.exec_path, '-C', file.path)
        output = subprocess.check_output(args)
        scan_result = []
        m = re.findall(self.search_pattern, output)
        if m is None:
            return None
        else:
            return '\n'.join(m) or None

    def store_results(self, processed_files):
        for file in processed_files:
            if processed_files[file] is not None:
                scanresult.add_file_copyright(self.conn, file.file_id, processed_files[file])


class NomosDeep(Nomos):

    """Same as Nomos, but unpacks archives in the file list.

    Regular Nomos treats every file as a monolith. This one will unpack
    those files that are archives, and scan the resulting directory structure.
    All licenses found for such an archive are treated as associated with
    the archive itself, rather than any of the files inside.

    Thus, Nomos and NomosDeep will return the same number of files scanned,
    but for those scanned files that are archive files, NomosDeep will likely
    return better results, at the cost of execution speed.
    """

    name = 'nomos_deep'

    def process_file(self, file):
        scan_result = set()
        if util.archive_type(file.path):
            with util.tempextract(file.path) as (tempdir, relpaths):
                abspaths = (os.path.join(tempdir, relpath) for relpath in relpaths)
                filepaths = (abspath for abspath in abspaths if os.path.isfile(abspath))
                for filepath in filepaths:
                    work_item = WorkItem(None, filepath)
                    this_result = super(NomosDeep, self).process_file(work_item)
                    scan_result.update(this_result)
        else:
            scan_result = super(NomosDeep, self).process_file(file)
        return scan_result


class DependencyCheck(Scanner):

    name = 'dependency_check'

    def __init__(self, conn):
        super(DependencyCheck, self).__init__(conn)
        self.exec_path = config.config['scanner_' + self.name + '_path']

    def run(self, package_id, package_root, package_file_path=None, rescan=False):
        # rescan is ignored
        package_path = package_file_path or package_root
        with util.tempdir() as tempdir:
            args = [
                self.exec_path,
                '--out', tempdir,
                '--format', 'XML',
                '--scan', package_path,
                '--app', 'none',
                '--noupdate'
                ]
            subprocess.check_call(args, stderr=open(os.devnull))
            with open(os.path.join(tempdir, 'dependency-check-report.xml')) as f:
                xml_data = f.read()
        cpes = DependencyCheck.parse_dependency_xml(xml_data)
        scanresult.add_cpes(self.conn, package_id, cpes)

    @staticmethod
    def as_list(item):
        if isinstance(item, list):
            return item
        else:
            return [item]

    @staticmethod
    def extract_cpe(item):
        if isinstance(item, OrderedDict):
            return item['#text']
        else:
            return item

    @staticmethod
    def strip_whitespace(s):
        return re.sub(r'(\n|\s+)', r' ', s)

    @staticmethod
    def get_cpes(dep):
        idents = DependencyCheck.as_list(dep.get('identifiers', {}).get('identifier', []))
        cpes = []
        for ident in idents:
            if ident['@type'] == 'cpe':
                cpes.append({
                    'cpe': ident['name'],
                    'confidence': ident['@confidence'],
                    })
        return cpes

    @staticmethod
    def parse_dependency_xml(xml_text):
        x = xmltodict.parse(xml_text)
        deps = []
        root_deps = x['analysis']['dependencies'] or {}
        for dep in DependencyCheck.as_list(root_deps.get('dependency', list())):
            deps.append({
                'sha1': dep['sha1'],
                'cpes': DependencyCheck.get_cpes(dep)
                })
        return deps

"""Table of scanners known to dosocs2.

All scanners here are recognized by the -s option on the command line.
"""
scanners = {
    'copyright': Copyright,
    'monk': Monk,
    'nomos': Nomos,
    'nomos_deep': NomosDeep,
    'dummy': Scanner,
    'dependency_check': DependencyCheck
    }
