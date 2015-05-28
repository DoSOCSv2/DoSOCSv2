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

    def lookup_or_add_file(self, path):
        '''Add file to the database if it does not exist. (Do not scan.)

        Return the new or existing file object in any case.
        '''
        sha1 = util.sha1(path)
        existing_file = (self.session.query(orm.File)
                         .filter(orm.File.sha1 == sha1)
                         .first()
                         )
        if existing_file is not None:
            return existing_file
        file_type_id = (self.session.query(orm.FileType)
                        .filter(orm.FileType.name == util.spdx_filetype(path))
                        .one().file_type_id
                        )
        file_params = {'sha1': sha1,
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

    def scan_file(self, path, scanner=scanners.nomos):
        '''Scan file for licenses, and add it to the DB if it does not exist.

        Return the file object.
        '''
        file = self.lookup_or_add_file(path)
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
        '''
        raise NotImplementedError

    def fetch_doc(self, docid):
        return self.session.query(orm.Document).get(docid)
