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

'''File level information in an SPDX object.'''

import MySQLdb
import scanners
import util

class File(object):
    def __init__(self):
        self.name = ''
        self.type = None
        self.checksum = ''
        self.license_concluded = 'NOASSERTION'
        self.license_info = []
        self.license_comments = None
        self.copyright_text = 'NOASSERTION'
        self.artifact_of_project_name = None
        self.artifact_of_project_homepage = None
        self.artifact_of_project_uri = None
        self.comment = None
        self.notice = None
        self.contributor = None
        self.dependency = None

    @classmethod
    def from_db_checksum(cls, connection_info, checksum):
        with MySQLdb.connect(**connection_info) as cursor:
            query = """
                SELECT pf.file_name,
                    pf.file_type,
                    pf.license_concluded,
                    pf.license_info_in_file,
                    pf.license_comments,
                    pf.file_copyright_text,
                    pf.artifact_of_project_name,
                    pf.artifact_of_project_homepage,
                    pf.artifact_of_project_uri,
                    pf.file_comment,
                    pf.file_notice,
                    pf.file_contributor,
                    pf.file_dependency
                FROM package_files AS pf
                WHERE pf.file_checksum = %s"""
            cursor.execute(query, (checksum,))
            result = cursor.fetchone()

        inst = cls()
        inst.checksum = checksum
        inst.name = result[0]
        inst.type = result[1]
        inst.license_concluded = result[2]
        inst.license_info = result[3].split(",")
        inst.license_comments = result[4]
        inst.copyright_text = result[5]
        inst.artifact_of_project_name = result[6]
        inst.artifact_of_project_home_page = result[7]
        inst.artifact_of_project_uri = result[8]
        inst.comment = result[9]
        inst.notice = result[10]
        inst.contributor = result[11]
        inst.dependency = result[12]
        return inst

    @classmethod
    def from_db_package(cls, connection_info, package_file_id, package_id):
        with MySQLdb.connect(**connection_info) as cursor:
            query = """
                SELECT pf.file_name,
                       pf.file_type,
                       pf.license_concluded,
                       pf.license_info_in_file,
                       pf.license_comments,
                       pf.file_copyright_text,
                       pf.artifact_of_project_name,
                       pf.artifact_of_project_homepage,
                       pf.artifact_of_project_uri,
                       pf.file_comment,
                       pf.file_notice,
                       pf.file_contributor,
                       pf.file_dependency,
                       pf.file_checksum
                FROM package_files AS pf
                LEFT JOIN doc_file_package_associations AS dfpa
                  ON pf.id = dfpa.package_file_id
                  AND dfpa.package_id = %s
                WHERE pf.id = %s
                """
            cursor.execute(query, (package_id, package_file_id))
            result = cursor.fetchone()
        
        inst.name = result[0]
        inst.type = result[1]
        inst.license_concluded = result[2]
        inst.license_info = result[3].split(",")
        inst.license_comments = result[4]
        inst.copyright_text = result[5]
        inst.artifact_of_project_name = result[6]
        inst.artifact_of_project_home_page = result[7]
        inst.artifact_of_project_uri = result[8]
        inst.comment = result[9]
        inst.notice = result[10]
        inst.contributor = result[11]
        inst.dependency = result[12]
        inst.checksum = result[13]
        return inst

    def store(self, connection_info, spdx_doc_id, package_id):
        return # temp
        fileId = self.isCached()

        '''If the file is not already in database then insert it'''
        if fileId == -1:
            '''Get id of next file'''
            sqlCommand = "SHOW TABLE STATUS LIKE 'package_files'"
            dbCursor.execute(sqlCommand)
            fileId = dbCursor.fetchone()[10]

            sqlCommand = """INSERT INTO package_files
                                    (file_name,
                                    file_type,
                                    file_copyright_text,
                                    artifact_of_project_name,
                                    artifact_of_project_homepage,
                                    artifact_of_project_uri,
                                    license_concluded,
                                    license_info_in_file,
                                    file_checksum,
                                    file_checksum_algorithm,
                                    license_comments,
                                    file_notice,
                                    file_contributor,
                                    file_dependency,
                                    file_comment,
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
                                    CURRENT_TIMESTAMP,
                                    CURRENT_TIMESTAMP)"""

            dbCursor.execute(sqlCommand, (self.fileName,
                                        self.fileType,
                                        self.fileCopyRightText,
                                        self.artifactOfProjectName,
                                        self.artifactOfProjectHomePage,
                                        self.artifactOfProjectURI,
                                        self.licenseConcluded,
                                        ','.join(self.licenseInfoInFile),
                                        self.fileChecksum,
                                        self.fileChecksumAlgorithm,
                                        self.licenseComments,
                                        self.fileNotice,
                                        self.fileContributor,
                                        self.fileDependency,
                                        self.fileComment)
                            )

        sqlCommand = """INSERT INTO doc_file_package_associations
                                    ( spdx_doc_id,
                                    package_id,
                                    package_file_id,
                                    relative_path,
                                    created_at,
                                    updated_at)
                        VALUES (%s,
                                %s,
                                %s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        dbCursor.execute(sqlCommand, (spdx_doc_id, package_id, fileId, self.fileRelativePath))

        sqlCommand = """INSERT INTO package_license_info_from_files
                                        (package_id,
                                        package_license_info_from_files,
                                        created_at,
                                        updated_at)
                        VALUES (%s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        '''Foreach license in the file, insert'''
        for license in self.licenseInfoInFile:
            dbCursor.execute(sqlCommand, (package_id, license))

        return fileId

    @staticmethod
    def get_id_by_checksum(connection_info, checksum):
        with MySQLdb.connect(**connection_info) as cursor:
            query = '''
                SELECT id
                FROM package_files
                WHERE file_checksum = %s'''
            cursor.execute(query, (checksum,))
            result = cursor.fetchone()
            if result is not None:
                return result[0]
            else:
                return None

    @classmethod
    def from_file(cls, connection_info, filename, scanner=scanners.nomos):
        checksum = util.sha1(filename)
        existing_id = File.get_id_by_checksum(connection_info, checksum)
        if existing_id is not None:
            return File.from_db_checksum(connection_info, checksum)
        else:
            inst = cls()
            inst.name = filename
            inst.checksum = checksum
            inst.license_info = [item[1] for item in scanner.scan(filename)]
            inst.license_comments = scanner.name + ': ' + ','.join(inst.license_info)
            inst.type = util.spdx_filetype(filename)
            return inst
