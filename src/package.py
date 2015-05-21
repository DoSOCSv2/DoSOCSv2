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

'''Package level information for the SPDX object.'''
import MySQLdb
import os
import hashlib


class Package(object):
    '''Initialize package object'''
    def __init__(self):
        self.name = ''
        self.version = None
        self.file_name = None
        self.supplier = None
        self.originator = None
        self.download_location = ''
        self.verification_code = ''
        self.checksum = ''
        self.home_page = None
        self.source_info = None
        self.license_concluded = 'NOASSERTION'
        self.license_info_from_files = []
        self.license_declared = 'NOASSERTION'
        self.license_comments = None
        self.copyright_text = ''
        self.summary = None
        self.description = None

        #if packagePath is not None:
        #    self.packageName = os.path.split(packagePath)[1]
        #    self.packageFileName = self.packageName

    def store(self, connection_info):
        '''inserts packageInformation into database.'''

        return  # temp
        sqlCommand = "SHOW TABLE STATUS LIKE 'packages'"
        dbCursor.execute(sqlCommand)
        packageId = dbCursor.fetchone()
        packageId = packageId[10]

        sqlCommand = """INSERT INTO packages
                                (package_name,
                                  package_file_name,
                                  package_download_location,
                                  package_copyright_text,
                                  package_version,
                                  package_description,
                                  package_summary,
                                  package_originator,
                                  package_supplier,
                                  package_license_concluded,
                                  package_license_declared,
                                  package_checksum,
                                  checksum_algorithm,
                                  package_home_page,
                                  package_source_info,
                                  package_license_comments,
                                  package_verification_code,
                                  package_verification_code_excluded_file,
                                  created_at,
                                  updated_at)
                        VALUES (%s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        dbCursor.execute(sqlCommand,
                          (self.packageName,
                           self.packageFileName,
                           self.packageDownloadLocation,
                           self.packageCopyrightText,
                           self.packageVersion,
                           self.packageDescription,
                           self.packageSummary,
                           self.packageOriginator,
                           self.packageSupplier,
                           self.packageLicenseConcluded,
                           self.packageLicenseDeclared,
                           self.packageChecksum,
                           self.packageChecksumAlgorithm,
                           self.packageHomePage,
                           self.packageSourceInfo,
                           self.packageLicenseComments,
                           self.packageVerificationCode,
                           self.packageVerificationCodeExcludedFile)
                        )

        sqlCommand = """INSERT INTO package_license_info_from_files
                                            (package_id,
                                            package_license_info_from_files,
                                            created_at,
                                            updated_at)
                        VALUES (%s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        for license_info in self.packageLicenseInfoFromFiles:
            dbCursor.execute(sqlCommand, (packageId, license_info))

        return packageId

    @classmethod
    def from_database(cls, connection_info, package_id):
        query = '''
            SELECT package_name,
                   package_version,
                   package_file_name,
                   package_supplier,
                   package_originator,
                   package_download_location,
                   package_verification_code,
                   package_checksum,
                   package_home_page,
                   package_source_info,
                   package_license_concluded,
                   package_license_declared,
                   package_license_comments,
                   package_copyright_text,
                   package_description,
                   package_summary
            FROM packages
            WHERE id = %s'''
        cursor.execute(query, (package_id,))
        result = dbCursor.fetchone()
        inst = cls()
        inst.name = result[0]
        inst.version = result[1]
        inst.file_name = result[2]
        inst.supplier = result[3]
        inst.originator = result[4]
        inst.download_location = result[5]
        inst.verification_code = result[6]
        inst.checksum = result[7]
        inst.home_page = result[8]
        inst.source_info = result[9]
        inst.license_concluded = result[10]
        inst.license_declared = result[11]
        inst.license_comments = result[12]
        inst.copyright_text = result[13]
        inst.description = result[14]
        inst.summary = result[15]
        return inst

    def getChecksum(self):
        with open(self.packagePath, 'rb') as fileIn:
            self.packageChecksum = hashlib.sha1(fileIn.read()).hexdigest()

    @staticmethod
    def get_id_by_checksum(self, connection_info, checksum):
        with MySQLdb.connect(**connection_info) as cursor:
            query = "SELECT id FROM packages WHERE package_checksum = %s"
            cursor.execute(query, (self.packageChecksum,))
            result = cursor.fetchone()
            if result is not None:
                return result[0]
            else:
                return None

    @staticmethod
    def gen_verification_code(sha1list):
        sha1list.sort()
        hashlib.sha1(''.join(sha1list)).hexdigest()
