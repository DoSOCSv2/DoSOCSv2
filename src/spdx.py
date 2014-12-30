#!/usr/bin/python
'''
<SPDX-License-Identifier: Apache-2.0>
Copyright 2014 University of Nebraska at Omaha (UNO)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import errno
import creatorInfo
import packageInfo
import licensingInfo
import fileInfo
import reviewerInfo
import os
import MySQLdb
import tempfile
import shutil
import settings
import tarfile
import zipfile
import sets
import shutil

'''
This contains the definition for the SPDX object.
'''

class SPDX:
    def __init__(self,
                 packagePath,
                 version="1.2",
                 dataLicense="CC-1.0",
                 documentComment=None,
                 creator=None,
                 creatorComment=None,
                 licenseListVersion=None,
                 packageVersion=None,
                 packageSupplier=None,
                 packageOriginator=None,
                 packageDownloadLocation="",
                 packageHomePage=None,
                 packageSourceInfo=None,
                 packageLicenseComments=None,
                 packageDescription=None),
                 scanOption=None):
        self.scanOption = scanOption
        self.packagePath = packagePath
        self.version = version
        self.dataLicense = dataLicense
        self.documentComment = documentComment
        self.creatorInfo = creatorInfo.creatorInfo( packagePath,
                                                    creator,
                                                    creatorComment,
                                                    licenseListVersion)
        self.packageInfo = packageInfo.packageInfo( packagePath,
                                                    packageVersion,
                                                    packageSupplier,
                                                    packageOriginator,
                                                    packageDownloadLocation,
                                                    packageHomePage,
                                                    packageSourceInfo,
                                                    packageLicenseComments,
                                                    packageDescription)
        self.licensingInfo = []
        self.fileInfo = []
        self.reviewerInfo = []

    def insertSPDX(self):
        '''insert SPDX doc into db'''
        spdxDocId = None

        with MySQLdb.connect(host=settings.database_host,
                             user=settings.database_user,
                             passwd=settings.database_pass,
                             db=settings.database_name) as dbCursor:
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

            dbCursor.execute(sqlCommand,(self.version,
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

        with MySQLdb.connect(host=settings.database_host,
                             user=settings.database_user,
                             passwd=settings.database_pass,
                             db=settings.database_name) as dbCursor:
            for files in self.fileInfo:
                files.insertFileInfo(spdxDocId, packageId, dbCursor)

        with MySQLdb.connect(    host=settings.database_host,
                                user=settings.database_user,
                                passwd=settings.database_pass,
                                db=settings.database_name) as dbCursor:
            for license in self.licensingInfo:
                license.insertLicensingInfo(spdxDocId, dbCursor)

        with MySQLdb.connect(    host=settings.database_host,
                                user=settings.database_user,
                                passwd=settings.database_pass,
                                db=settings.database_name) as dbCursor:
            ''' Insert Reviewer Information '''
            for reviewer in self.reviewerInfo:
                reviewer.insertReviewerInfo(spdxDocId, dbCursor)
        return spdxDocId
    
    def outputSPDX_TAG(self):
        '''output SPDX in tag format'''
        output = ""
        output += "SPDXVersion: " + str(self.version) + '\n'
        output += "DataLicense: " + str(self.dataLicense) + '\n'
        output += "Document Comment: <text>"
        output += str(self.documentComment)
        output += "</text>\n"
        output += "\n\n"
        output += "## Creation Information\n\n"
        output += str(self.creatorInfo.outputCreatorInfo_TAG())
        output += "\n\n"
        output += "## Package Information\n\n"
        output += str(self.packageInfo.outputPackageInfo_TAG())
        output += "\n\n"
        output += "## File Information\n\n"

        for files in self.fileInfo:
            output += str(files.outputFileInfo_TAG()) + "\n\n"

        output += "## License Information\n\n"

        for licenses in self.licensingInfo:
            output += str(licenses.outputLicensingInfo_TAG()) + "\n"

        if len(self.reviewerInfo) > 0:
            output += "## Reviewer Information\n\n"
            for reviewer in self.reviewerInfo:
                output += str(reviewer.outputReviewerInfo_TAG())

        return output

    def outputSPDX_RDF(self):
        '''Render the spdx object in rdf format'''
        output = ""
        output += '<SpdxDocument rdf:about="">\n'
        output += '\t<specVersion>' + str(self.version) + '</specVersion>\n'
        output += '\t<dataLicense rdf:resource="' + str(self.dataLicense) + '" />\n'
        output += '\t<rdfs:comment>'
        output += str(self.documentComment)
        output += '</rdfs:comment>\n'
        output += '\t<CreationInfo>\n'
        output += str(self.creatorInfo.outputCreatorInfo_RDF())
        output += '\t</CreationInfo>\n'
        output += '\t<Package rdf:about="">\n'
        output += str(self.packageInfo.outputPackageInfo_RDF())
        output += '\t</Package>\n'

        for files in self.fileInfo:
            output += '\t<File rdf:about="">\n'
            output += str(files.outputFileInfo_RDF())
            output += '\t</File>\n'

        if len(self.licensingInfo) > 0:
            for licenses in self.licensingInfo:
                output += '\t<ExtractedLicensingInfo>\n'
                output += str(licenses.outputLicensingInfo_RDF())
                output += '\t</ExtractedLicensingInfo>\n'

        output += '</SpdxDocument>\n'

        return output

    def outputSPDX_JSON(self):
        '''Render the spdx object in json format'''
        output =  '{\n'
        output += '\t"spdxDocument" : {\n'
        output += '\t\t"specVersion" : "' + str(self.version) + '",\n'
        output += '\t\t"dataLicense" : "' + str(self.dataLicense) + '",\n'
        output += '\t\t"comment" : "' + str(self.documentComment) + '",\n'
        output += '\t\t"creationInfo" :' + self.creatorInfo.outputCreatorInfo_JSON() + ',\n'
        output += '\t\t"packageInfo" :' + self.packageInfo.outputPackageInfo_JSON() + ',\n'
        output += '\t\t"fileInfo" : [\t'
        count = 1
        for files in self.fileInfo:
            output += '\t\t\t' + files.outputFileInfo_JSON()
            if count != len(self.fileInfo):
                output += ','
            output += '\n'
            count += 1
        output += '\t\t],\n'
        output += '\t\t"licensingInfo" : [\t'
        count = 1
        for licenses in self.licensingInfo:
            output += '\t\t\t' + licenses.outputLicensingInfo_JSON()
            if count != len(self.licensingInfo):
                output += ','
            output += '\n'
            count += 1
        output += '\t\t]\n'
        output += '\t}\n'
        output += '}\n'

        return output

    def getSPDX(self, spdx_doc_id):
        '''Generates the entire object from the database.'''

        with MySQLdb.connect(    host=settings.database_host,
                                user=settings.database_user,
                                passwd=settings.database_pass,
                                db=settings.database_name) as dbCursor:
            sqlCommand = """SELECT     spdx_version,
                                    data_license,
                                    document_comment
                            FROM spdx_docs
                            WHERE id = %s"""
            dbCursor.execute(sqlCommand, (spdx_doc_id))
            rows = dbCursor.fetchone()

            if rows != None:
                self.version = rows[0]
                self.dataLicense = rows[1]
                self.documentComment = rows[2]
            else:
                print "SPDX Document not found in database."
                return False

            self.creatorInfo.getCreatorInfo(spdx_doc_id, dbCursor)
            self.packageInfo.getPackageInfo(spdx_doc_id, dbCursor)

            '''Get File Info'''
            sqlCommand = """SELECT dfpa.package_file_id,pf.file_checksum
                            FROM doc_file_package_associations AS dfpa
                                    LEFT OUTER JOIN package_files AS pf ON pf.id = dfpa.package_file_id
                            WHERE spdx_doc_id = %s"""
            dbCursor.execute(sqlCommand, spdx_doc_id)

            for row in dbCursor:
                if row != None:
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

                    for y in xrange(0, dbCursor.rowcount):
                        tempLicensingInfo = licensingInfo.licensingInfo()
                        row2 = dbCursor.fetchone()
                        if row2 != None:
                            tempLicensingInfo.getLicensingInfo(row2[0], dbCursor)
                            self.licensingInfo.append(tempLicensingInfo)

            '''Get Reviewer Info'''
            sqlCommand = """SELECT id FROM reviewers WHERE spdx_doc_id = %s"""
            dbCursor.execute(sqlCommand, spdx_doc_id)
            for x in xrange(0, dbCursor.rowcount):
                tempReviewerInfo = reviewerInfo.reviewerInfo()
                tempReviewerInfo.getReviwerInfo(dbCursorfetchone()[0], dbCursor)
                self.reviewerInfo.append(tempReviewerInfo)

    def generateSPDXDoc(self):
        '''Generates the entire structure by querying and scanning the files.'''
        extractTo = tempfile.mkdtemp()
        ninka_out = tempfile.NamedTemporaryFile()
        foss_out = tempfile.NamedTemporaryFile()
        licenseCounter = 0
        scanners = []
        licensesFromFiles = []
        sha1Checksums = []
        path = ""

        with MySQLdb.connect(    host=settings.database_host,
                                user=settings.database_user,
                                passwd=settings.database_pass,
                                db=settings.database_name) as dbCursor:
            if tarfile.is_tarfile(self.packagePath):
                '''If it is a tar file, use tarfile component'''
                archive = tarfile.open(self.packagePath)
                archive.extractall(extractTo)
                for fileName in archive.getnames():
                    if os.path.isfile(os.path.join(extractTo, fileName)):
                        tempFileInfo = fileInfo.fileInfo(os.path.join(extractTo, fileName), os.path.join(path, fileName))
                        tempFileInfo.populateFileInfo(scanOption)
                        tempLicenseInfo = licensingInfo.licensingInfo(
                                                        "LicenseRef-" + str(licenseCounter),
                                                        tempFileInfo.extractedText,
                                                        tempFileInfo.licenseInfoInFile[0],
                                                        "",
                                                        tempFileInfo.licenseComments,
                                                        tempFileInfo.fileChecksum
                                            )
                        existingLicense = tempLicenseInfo.compareLicensingInfo(self.licensingInfo)
                        if existingLicense == None:
                            self.packageInfo.packageLicenseInfoFromFiles.append(tempLicenseInfo.licenseId)
                            licenseCounter += 1
                        else:
                            tempLicenseInfo = licensingInfo.licensingInfo(existingLicense.licenseId, 
                                                                          existingLicense.extractedText,
                                                                          existingLicense.licenseName,
                                                                          existingLicense.licenseCrossReference,
                                                                          existingLicense.licenseComment,
                                                                          tempFileInfo.fileChecksum)
                        self.licensingInfo.append(tempLicenseInfo)
                        sha1Checksums.append(tempFileInfo.fileChecksum)
                        self.fileInfo.append(tempFileInfo)
                        path = ""
                    else:
                        path = os.path.join(path, fileName)
    
            elif zipfile.is_zipfile(self.packagePath):
                '''If it is a zip file, use zipfile component'''
                archive = zipfile.ZipFile(self.packagePath, "r")
                archive.extractall(extractTo)
                for fileName in archive.namelist():
                    if os.path.isfile(os.path.join(extractTo, fileName)):
                        tempFileInfo = fileInfo.fileInfo(os.path.join(extractTo, fileName), os.path.join(path, fileName))
                        tempFileInfo.populateFileInfo()
                        tempLicenseInfo = licensingInfo.licensingInfo(
                                                        "LicenseRef-" + str(licenseCounter),
                                                        tempFileInfo.extractedText,
                                                        tempFileInfo.licenseInfoInFile[0],
                                                        "",
                                                        tempFileInfo.licenseComments,
                                                        tempFileInfo.fileChecksum
                                        )
                        existingLicense = tempLicenseInfo.compareLicensingInfo(self.licensingInfo)
                        if existingLicense == None:
                            self.packageInfo.packageLicenseInfoFromFiles.append(tempLicenseInfo.licenseId)
                            licenseCounter += 1
                        else:
                            tempLicenseInfo = licensingInfo.licensingInfo(existingLicense.licenseId, 
                                                                          existingLicense.extractedText,
                                                                          existingLicense.licenseName,
                                                                          existingLicense.licenseCrossReference,
                                                                          existingLicense.licenseComment,
                                                                          tempFileInfo.fileChecksum)
                        self.licensingInfo.append(tempLicenseInfo)
                        sha1Checksums.append(tempFileInfo.fileChecksum)
                        self.fileInfo.append(tempFileInfo)
                        path = ""
                    else:
                        path = os.path.join(path, fileName)

        self.packageInfo.generatePackageInfo(sha1Checksums)
        ninka_out.close()
        foss_out.close()
        '''Delete the temporary files.'''
        shutil.rmtree(extractTo)
