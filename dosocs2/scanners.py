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
from collections import namedtuple

from sqlalchemy import select, and_
import xmltodict

from . import util
from . import scanresult
from . import schema as db
from . import spdxdb
from .config import config


WorkItem = namedtuple('WorkItem', ['file_id', 'path'])


class Scanner(object):

    name = 'dummy'

    def __init__(self, conn):
        self.conn = conn
        self.register()

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

    def run(self, package_id, package_root, package_file_path=None, rescan=False):
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
        # override in subclass
        pass

    def store_results(self, processed_files):
        # override in subclass
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

    def file_is_already_done(self, file):
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


class NomosDeep(Nomos):

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
        self.exec_path = config['dependency_check']['path']

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


scanners = {
    'nomos': Nomos,
    'nomos_deep': NomosDeep,
    'dummy': Scanner,
    'dependency_check': DependencyCheck
    }
