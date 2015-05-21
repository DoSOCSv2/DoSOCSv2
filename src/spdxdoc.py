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

from package import Package
from file import File
#from review import Review
#import licensing
import reviewerInfo
import licensingInfo
import os
import MySQLdb
import tempfile
import shutil
import tarfile
import util


'''Definition for the SPDX object.'''


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
        return  # temp
        '''insert SPDX doc into db'''
        spdxDocId = None

        with MySQLdb.connect(**settings.database) as dbCursor:
            '''get spdx doc id'''
            sqlCommand = "SHOW TABLE STATUS LIKE 'spdx_docs'"
            dbCursor.execute(sqlCommand)
            spdxDocId = dbCursor.fetchone()[10]

            '''Insert spdx info'''
            sqlCommand = """INSERT INTO spdx_docs(spdx_version,
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

            dbCursor.execute(sqlCommand, (self.version,
                                         self.dataLicense,
                                         self.packageInfo.packageName,
                                         'SQL',
                                         self.packageInfo.fileSize,
                                         self.documentComment
                                         )
                            )

            ''' Insert Creator Information '''
            creatorId = self.creatorInfo.insertCreatorInfo(spdxDocId, dbCursor)
            ''' Insert Package Information '''
            packageId = self.packageInfo.insertPackageInfo(dbCursor)
            ''' Insert File Information '''

        with MySQLdb.connect(**settings.database) as dbCursor:
            for files in self.fileInfo:
                files.insertFileInfo(spdxDocId, packageId, dbCursor)

        with MySQLdb.connect(**settings.database) as dbCursor:
            for license in self.licensingInfo:
                license.insertLicensingInfo(spdxDocId, dbCursor)

        with MySQLdb.connect(**settings.database) as dbCursor:
            ''' Insert Reviewer Information '''
            for reviewer in self.reviewerInfo:
                reviewer.insertReviewerInfo(spdxDocId, dbCursor)
        return spdxDocId

    def render(self, templatefile):
        return util.render_template(templatefile, self.__dict__)

    @classmethod
    def from_db_docid(self, connection_info, docid):
        '''Generates the entire object from the database.'''

        with MySQLdb.connect(**connection_info) as cursor:
            query = '''
                SELECT spdx_version,
                       data_license,
                       document_comment
                FROM spdx_docs
                WHERE id = %s'''
            cursor.execute(query, (spdx_doc_id,))
            rows = cursor.fetchone()

            if rows is not None:
                self.version = rows[0]
                self.data_license = rows[1]
                self.document_comment = rows[2]
            else:
                print("SPDX Document not found in database.")
                return False

            self.creatorInfo.getCreatorInfo(spdx_doc_id, dbCursor)
            self.package = Package.from_db_docid(connection_info, docid)

            '''Get File Info'''
            sqlCommand = """SELECT dfpa.package_file_id,pf.file_checksum
                            FROM doc_file_package_associations AS dfpa
                                    LEFT OUTER JOIN package_files AS pf ON pf.id = dfpa.package_file_id
                            WHERE spdx_doc_id = %s"""
            dbCursor.execute(sqlCommand, spdx_doc_id)

            for row in dbCursor:
                if row is not None:
                    tempFileInfo = fileInfo.fileInfo()
                    tempFileInfo.getFileInfo(row[0], self.packageInfo.packageId, dbCursor)
                    self.fileInfo.append(tempFileInfo)

                    '''Get the license information for this file'''
                    sqlCommand = """SELECT dla.license_id
                                    FROM licensings AS l
                                    LEFT OUTER JOIN doc_license_associations AS dla
                                            ON l.doc_license_association_id = dla.id
                                    WHERE l.package_file_id = %s"""

                    dbCursor.execute(sqlCommand, row[0])

                    for y in range(0, dbCursor.rowcount):
                        tempLicensingInfo = licensingInfo.licensingInfo()
                        row2 = dbCursor.fetchone()
                        if row2 is not None:
                            tempLicensingInfo.getLicensingInfo(row2[0], dbCursor)
                            self.licensingInfo.append(tempLicensingInfo)

            '''Get Reviewer Info'''
            sqlCommand = """SELECT id FROM reviewers WHERE spdx_doc_id = %s"""
            dbCursor.execute(sqlCommand, spdx_doc_id)
            for x in range(0, dbCursor.rowcount):
                tempReviewerInfo = reviewerInfo.reviewerInfo()
                tempReviewerInfo.getReviwerInfo(dbCursorfetchone()[0], dbCursor)
                self.reviewerInfo.append(tempReviewerInfo)

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
