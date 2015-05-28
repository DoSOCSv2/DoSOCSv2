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

from sqlalchemy.orm.exc import NoResultFound
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
        self.session = orm.load_session()

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
        self.session.commit()
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
        self.session.commit()
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
        self.session.commit()
        return file


def scan_package(package_path):
    pass


class SPDXDoc:
    def __init__(self, version='SPDX-1.2', data_license='CC0-1.0'):
        self.version = version
        self.data_license = data_license
        self.licenses = []
        self.files = []
        self.reviews = []
        self.document_comment = None
        self.creator = None
        self.package = None

    def store(self, connection_info):
        doc_id = None

        with MySQLdb.connect(**connection_info) as cursor:
            '''get spdx doc id'''
            query = "SHOW TABLE STATUS LIKE 'spdx_docs'"
            cursor.execute(query)
            doc_id = cursor.fetchone()[10]

            '''Insert spdx info'''
            query = """INSERT INTO spdx_docs(spdx_version,
                                                data_license,
                                                upload_file_name,
                                                upload_content_type,
                                                upload_file_size,
                                                upload_updated_at,
                                                document_comment,
                                                created_at,updated_at)
                            VALUES (%s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    CURRENT_TIMESTAMP,
                                    %s,
                                    CURRENT_TIMESTAMP,
                                    CURRENT_TIMESTAMP)"""

            cursor.execute(query, (self.version,
                                         self.data_license,
                                         self.package.name,
                                         'SQL',
                                         0,
                                         self.document_comment
                                         )
                            )

            ''' Insert Creator Information '''
            creator_id = self.creator.store(connection_info, doc_id)
            ''' Insert Package Information '''
            package_id = self.package.store(connection_info)
            ''' Insert File Information '''

        with MySQLdb.connect(**connection_info) as cursor:
            for file in self.files:
                file.store(connection_info, doc_id, package_id)

        with MySQLdb.connect(**connection_info) as cursor:
            for license in self.licenses:
                license.store(connection_info, doc_id)

        with MySQLdb.connect(**connection_info) as cursor:
            ''' Insert Reviewer Information '''
            for review in self.reviews:
                review.store(connection_info, doc_id)
        return doc_id

    def render(self, templatefile):
        return util.render_template(templatefile, self.__dict__)

    @classmethod
    def from_db_docid(self, connection_info, docid):
        raise NotImplementedError

    @classmethod
    def from_package(cls, connection_info, package_path):
        license_counter = 0
        licenses_from_files = []
        checksums = []
        path = ""

        self = cls()

        if tarfile.is_tarfile(package_path):
            self.package = Package()
            tempdir = tempfile.mkdtemp()
            with tarfile.open(package_path) as archive:
                archive.extractall(tempdir)
                filenames = archive.getnames()
            absolute_filenames = [os.path.join(tempdir, filename)
                                  for filename in filenames
                                  ]
            for filename in absolute_filenames:
                if os.path.isfile(filename):
                    fileinfo = File.from_file(connection_info, filename)
                    tempLicenseInfo = licensingInfo.licensingInfo(
                                                    "LicenseRef-" + str(license_counter),
                                                    '',
                                                    fileinfo.license_info[0],
                                                    '',
                                                    fileinfo.license_comments,
                                                    fileinfo.checksum
                                        )
                    #existingLicense = tempLicenseInfo.compareLicensingInfo(self.licensingInfo)
                    existingLicense = None
                    if existingLicense is None:
                        self.package.license_info_from_files.append(tempLicenseInfo.licenseId)
                        license_counter += 1
                    else:
                        tempLicenseInfo = licensingInfo.licensingInfo(existingLicense.licenseId,
                                                                        existingLicense.extractedText,
                                                                        existingLicense.licenseName,
                                                                        existingLicense.licenseCrossReference,
                                                                        existingLicense.licenseComment,
                                                                        fileinfo.checksum)
                    self.licenses.append(tempLicenseInfo)
                    checksums.append(fileinfo.checksum)
                    self.files.append(fileinfo)
                    # convert filename to package-relative filename
                    fileinfo.name = '.' + fileinfo.name[len(tempdir):]
            shutil.rmtree(tempdir)

        self.package.verification_code = Package.gen_verification_code(checksums)
        return self
