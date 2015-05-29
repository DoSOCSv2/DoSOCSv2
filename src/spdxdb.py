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

import itertools
import orm
import os
import scanners
import shutil
import tarfile
import tempfile
import util
import uuid


class SPDXDB:
    def __init__(self):
        pass

    def __enter__(self):
        self.session = orm.Session()
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()

    def lookup_by_sha1(self, obj_type, sha1):
        '''Lookup object by SHA-1 sum and return the object, or None.'''
        # Maybe shouldn't be using first() here?
        # Freak occurence of sha1 collision probably won't happen.
        # But if it does, this will give nondeterministic results.
        # (although, you will have bigger problems...)
        return (
            self.session.query(obj_type)
            .filter(obj_type.sha1 == sha1)
            .first()
            )

    def lookup_or_add_license(self, short_name):
        '''Add license to the database if it does not exist.

        Return the new or existing license object in any case.
        '''
        existing_license = (self.session.query(orm.License)
                            .filter(orm.License.short_name == short_name)
                            .first()
                            )
        if existing_license is not None:
            return existing_license
        license_identifier = 'LicenseRef-' + str(uuid.uuid4())
        license_params = {'name': 'NOASSERTION',
                          'short_name': short_name,
                          'cross_reference': '',
                          'comment': '',
                          'is_spdx_official': False,
                          'license_identifier': license_identifier
                          }
        new_license = orm.License(**license_params)
        self.session.add(new_license)
        self.session.flush()
        return new_license

    def _create_file(self, path, sha1):
        file_type_id = (
            self.session.query(orm.FileType)
            .filter(orm.FileType.name == util.spdx_filetype(path))
            .one().file_type_id
            )
        file_params = {
            'sha1': sha1,
            'file_type_id': file_type_id,
            'copyright_text': '',
            'project_id': None,
            'comment': '',
            'notice': ''
            }
        new_file = orm.File(**file_params)
        self.session.add(new_file)
        self.session.flush()
        return new_file

    def scan_file(self, path, scanner=scanners.nomos):
        '''Scan file for licenses, and add it to the DB if it does not exist.

        Return the file object.

        If the file is cached, return the cached file object, and do not
        scan.
        '''
        sha1 = util.sha1(path)
        file = self.lookup_by_sha1(orm.File, sha1)
        if file is not None:
            return file
        file = self._create_file(path, sha1)
        if scanner is not None:
            shortnames_found = [item[1] for item in scanner.scan(path)]
            licenses_found = [self.lookup_or_add_license(shortname)
                              for shortname in shortnames_found
                              ]
            license_comment = scanner.name + ': ' + ','.join(shortnames_found)
            for license in licenses_found:
                file_license_params = {'file_id': file.file_id,
                                       'license_id': license.license_id,
                                       'extracted_text': '',
                                       'license_comment': license_comment
                                       }
                new_file_license = orm.FileLicense(**file_license_params)
                self.session.add(new_file_license)
        self.session.flush()
        return file

    def scan_package(self, path, scanner=scanners.nomos):
        '''Scan package for licenses. Add it and all files to the DB.

        Return the package object.

        Only scan if the package is not already cached (by SHA-1).
        '''
        package_params = {
            'name': '',
            'version': '',
            'file_name': path,
            'supplier': '',
            'originator': '',
            'download_location': '',
            'verification_code': '',  # filled in later
            'ver_code_excluded_file_id': None,
            'sha1': util.sha1(path),
            'home_page': '',
            'source_info': '',
            'concluded_license_id': None,
            'declared_license_id': None,
            'license_comment': '',
            'copyright_text': '',
            'summary': '',
            'description': '',
            'comment': ''
            }
        new_package = orm.Package(**package_params)
        self.session.add(new_package)
        with util.tempextract(path) as (tempdir, relpaths):
            abspaths = [os.path.join(tempdir, path) for path in relpaths]
            hashes = []
            new_package_files = []
            for relpath, abspath in itertools.izip(relpaths, abspaths):
                if not os.path.isfile(abspath):
                    continue
                fileobj = self.scan_file(abspath, scanner)
                hashes.append(fileobj.sha1)
                package_file_params = {
                    'package_id': new_package.package_id,
                    'file_id': fileobj.file_id,
                    'concluded_license_id': None,
                    'file_name': os.path.join(os.curdir, relpath)
                    }
                new_package_file = orm.PackageFile(**package_file_params)
                new_package_files.append(new_package_file)
        new_package.verification_code = util.gen_ver_code(hashes)
        self.session.add_all(new_package_files)
        self.session.flush()
        return new_package

    def fetch_doc(self, docid):
        return self.session.query(orm.Document).get(docid)
