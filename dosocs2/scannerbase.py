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

"""Generic scanner facilities.

Includes Scanner base classes and the WorkItem class.
"""

import os
import re
import string
from collections import namedtuple

from sqlalchemy import select, and_

from . import schema as db
from . import spdxdb


"""A file (already registered) to be processed by a scanner."""
WorkItem = namedtuple('WorkItem', ['file_id', 'path'])


class Scanner(object):

    """Base class for connectors to external scanning tools.

    Any new connectors should inherit from Scanner or one of its subclasses,
    and at least override process_file(), store_results(), and the 'name'
    property.

    """

    """Name for this scanner, used in all contexts (including the database).

    All scanner names must be unique, thus subclasses must override this
    property. Not doing so will lead to strange results.
    """
    name = None

    def __init__(self, conn, config):
        """Initialize Scanner object.

        Register the scanner in the database if it is not already registered.
        Other initialization may be done here by subclasses.
        """
        self.conn = conn
        self.register()
        ignore_string = config.get('scanner_' + self.name + '_ignore')
        if ignore_string is not None:
            self.ignore_pattern = re.compile(ignore_string)
        else:
            self.ignore_pattern = None

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
            if self.ignore_pattern is not None:
                if re.match(self.ignore_pattern, file.path):
                    continue
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

        In the base Scanner class, this method raises NotImplementedError,
        so it must be overridden in a subclass.
        """
        raise NotImplementedError

    def store_results(self, processed_files):
        """Store scan results in the database. Return None.

        Arguments:
        processed_files -- A mapping (dictionary) of WorkItems to scan result
          objects.  The nature of these scan result objects depends on which
          scanner is being called.

        In the base Scanner class, this method raises NotImplementedError,
        so it must be overridden in a subclass.
        """
        raise NotImplementedError

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
    whose result is a dictionary mapping each license short name to the
    extracted text found for that license.

    New connectors to external license scanners should inherit from this and
    not from Scanner.
    """

    @staticmethod
    def lookup_license(conn, short_name):
        query = (
            select([db.licenses])
            .where(db.licenses.c.short_name == short_name)
            )
        [result] = conn.execute(query).fetchall() or [None]
        if result is None:
            return result
        else:
            return dict(**result)

    @staticmethod
    def lookup_or_add_license(conn, short_name, comment=None):
        '''Add license to the database if it does not exist.

        Return the new or existing license object in any case.
        '''
        transtable = string.maketrans('()[]<>', '------')
        short_name = string.translate(short_name, transtable)
        existing_license = FileLicenseScanner.lookup_license(conn, short_name)
        if existing_license is not None:
            return existing_license
        new_license = {
            # correct long name is never known for found licenses
            'name': None,
            'short_name': short_name,
            'cross_reference': '',
            'comment': comment or '',
            'is_spdx_official': False,
            }
        new_license['license_id'] = spdxdb.insert(conn, db.licenses, new_license)
        return new_license

    @staticmethod
    def add_file_licenses(conn, rows):
        to_add = {}
        for file_license_params in rows:
            query = (
                select([db.files_licenses])
                .where(
                    and_(
                        db.files_licenses.c.file_id == file_license_params['file_id'],
                        db.files_licenses.c.license_id == file_license_params['license_id']
                        )
                    )
                )
            [already_exists] = conn.execute(query).fetchall() or [None]
            if already_exists is None:
                key = file_license_params['file_id'], file_license_params['license_id']
                to_add[key] = file_license_params
        spdxdb.bulk_insert(conn, db.files_licenses, list(to_add.values()))

    def store_results(self, processed_files):
        licenses_to_add = []
        for (file, licenses_extracted) in processed_files.iteritems():
            licenses = []
            for license_name in licenses_extracted:
                license_kwargs = {
                    'conn': self.conn,
                    'short_name': license_name,
                    'comment': 'found by ' + self.name
                    }
                lic = FileLicenseScanner.lookup_or_add_license(**license_kwargs)
                licenses.append((lic, licenses_extracted[license_name]))
            for (license, extracted_text) in licenses:
                file_license_kwargs = {
                    'file_id': file.file_id,
                    'license_id': license['license_id'],
                    'extracted_text': extracted_text or ''
                    }
                licenses_to_add.append(file_license_kwargs)
        FileLicenseScanner.add_file_licenses(self.conn, licenses_to_add)
