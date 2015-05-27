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

'''License level information in the SPDX object.'''
import MySQLdb
import settings

class licensingInfo:
    def __init__(self,
                 licenseId=None,
                 extractedText=None,
                 licenseName=None,
                 licenseCrossReference=None,
                 licenseComment=None,
                 fileChecksum=None):
        self.licenseId = licenseId
        self.extractedText = extractedText
        self.licenseName = licenseName
        self.licenseCrossReference = licenseCrossReference
        self.licenseComment = licenseComment
        self.fileChecksum = fileChecksum

    def insertLicensingInfo(self,
                            spdx_doc_id,
                            dbCursor,
                            osi_approved="",
                            standard_license_header=""):
        '''inserts licensingInfo into database'''
        '''Get File Id'''
        sqlCommand = """SELECT id
                        FROM package_files
                        WHERE file_checksum = %s"""
        dbCursor.execute(sqlCommand, (self.fileChecksum))
        package_file_id = dbCursor.fetchone()[0]

        '''Get id of license'''
        sqlCommand = """SHOW TABLE STATUS LIKE 'licenses'"""
        dbCursor.execute(sqlCommand)
        licenseId = dbCursor.fetchone()[10]

        sqlCommand = """INSERT INTO licenses (extracted_text,
                                                license_name,
                                                osi_approved,
                                                standard_license_header,
                                                license_cross_reference,
                                                created_at, updated_at)
                        VALUES (%s,
                                %s,
                                %s,
                                %s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        dbCursor.execute(sqlCommand, (self.extractedText,
                                      self.licenseName,
                                      osi_approved,
                                      standard_license_header,
                                      self.licenseCrossReference)
                         )

        '''Get doc_license_association_id'''
        sqlCommand = """SHOW TABLE STATUS LIKE 'doc_license_associations'"""
        dbCursor.execute(sqlCommand)
        docLicenseAssoc = dbCursor.fetchone()[10]

        sqlCommand = """INSERT INTO doc_license_associations
                                                    (spdx_doc_id,
                                                    license_id,
                                                    license_identifier,
                                                    license_name,
                                                    license_comments,
                                                    created_at,
                                                    updated_at)
                        VALUES (%s,
                                %s,
                                %s,
                                %s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        dbCursor.execute(sqlCommand, (spdx_doc_id,
                                      licenseId,
                                      self.licenseId,
                                      self.licenseName,
                                      self.licenseComment)
                         )

        sqlCommand = """INSERT INTO licensings (package_file_id,
                                                juncture,
                                                doc_license_association_id,
                                                created_at,
                                                updated_at)
                        VALUES (%s,
                                "",
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        dbCursor.execute(sqlCommand, (package_file_id, docLicenseAssoc))

        return licenseId

    def getLicensingInfo(self, doc_license_association_id, dbCursor):
        '''populates licensingInfo from database'''
        sqlCommand = """SELECT dla.license_identifier,
                                dla.license_name,
                                dla.license_comments,
                                l.extracted_text,
                                l.license_cross_reference
                        FROM doc_license_associations AS dla
                            INNER JOIN licenses AS l ON dla.license_id = l.id
                        WHERE dla.id = %s"""
        dbCursor.execute(sqlCommand, (doc_license_association_id))

        queryReturn = dbCursor.fetchone()
        if queryReturn is not None:
            self.licenseId = queryReturn[0]
            self.licenseName = queryReturn[1]
            self.licenseComment = queryReturn[2]
            self.extractedText = queryReturn[3]
            self.licenseCrossReference = queryReturn[4]

    def compareLicensingInfo(self, altLicensingInfoList):
        for altLicensingInfo in altLicensingInfoList:
            if(self.extractedText == altLicensingInfo.extractedText):
                if(self.licenseName == altLicensingInfo.licenseName):
                    if(self.licenseCrossReference == altLicensingInfo.licenseCrossReference):
                        if(self.licenseComment == altLicensingInfo.licenseComment):
                            return self
        return None
