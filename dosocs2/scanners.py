# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2015 University of Nebraska Omaha and other contributors.

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

'''Interfaces to external scanning tools.

scan_file() and scan_directory() must return a dictionary mapping a relative
file path (starting with '.') to a set of license short names. These license
names do not necessarily have to be on the SPDX license list.

scan_file(path) -> {str: {str}} or None
scan_directory(path) -> {str: {str}} or None
'''

import os
import re
import subprocess
from collections import defaultdict, namedtuple

from sqlalchemy import select, and_

from . import util
from . import schema as db
from . import spdxdb
from .config import config

WorkItem = namedtuple('WorkItem', ['file_id', 'path'])

class Scanner(object):

    name = 'dummy'

    def __init__(self, conn):
        self.conn = conn

    def get_file_list(self, package_id, package_root):
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

    def run(self, package_id, package_path):
        # add package-level checking for "already done"
        self.register()
        all_files = self.get_file_list(package_id, package_path)
        processed_files = set()
        not_processed_files = set()
        for file in all_files:
            if not self.is_already_done(file):
                self.process_file(file)
                processed_files.add(file)
            else:
                not_processed_files.add(file)
        import pprint; pprint.pprint(processed_files)
        self.mark_done(processed_files)

    def process_file(self, file):
        pass

    def register(self):
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

    def is_already_done(self, file):
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

    def mark_done(self, files):
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


class Nomos(Scanner):

    name = 'nomos'

    def __init__(self, conn):
        super(Nomos, self).__init__(conn)
        self.exec_path = config['nomos']['path']
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


class NomosDeep(Scanner):

    name = 'nomos_deep'

    def __init__(self):
        self._nomos = Nomos()

    def scan_file(self, path):
        if util.archive_type(path):
            scan_result = set()
            with util.tempextract(path) as (tempdir, relpaths):
                unfiltered_results = self._nomos.scan_directory(tempdir)
            for this_result in unfiltered_results.values():
                scan_result.update(this_result)
            return {path: scan_result}
        else:
            return self._nomos.scan_file(path)

    def scan_directory(self, path):
        scan_result = {}
        for filepath in util.allpaths(path):
            if os.path.isfile(filepath):
                scan_result.update(self.scan_file(filepath))
        return scan_result


scanners = {
    'nomos': Nomos,
    'nomos_deep': NomosDeep,
    'dummy': Scanner
    }
