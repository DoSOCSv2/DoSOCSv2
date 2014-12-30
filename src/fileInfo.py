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

'''Defines the file level information in an spdx object.'''
import MySQLdb
import settings
import hashlib
import subprocess
import sys
import os
import output_parser
from signal import signal, SIGPIPE, SIG_DFL
from mimetypes import MimeTypes


class fileInfo:
    def __init__(self, filePath=None, fileRelativePath = ""):
        self.filePath = filePath
        self.fileType = None
        self.fileChecksum = None
        self.fileChecksumAlgorithm = "SHA1"
        self.licenseConcluded = "NO ASSERTION"
        self.licenseInfoInFile = []
        self.licenseComments = ""
        self.fileCopyRightText = ""
        self.artifactOfProjectName = ""
        self.artifactOfProjectHomePage = ""
        self.artifactOfProjectURI = ""
        self.fileComment = ""
        self.fileNotice = ""
        self.fileContributor = ""
        self.fileDependency = ""
        self.fileRelativePath = fileRelativePath
        self.extractedText = ""

        if self.filePath != None:
            self.getChecksum()
            self.fileName = os.path.split(filePath)[1]

    def getFileInfo(self, package_file_id, package_id, dbCursor):
        '''populates fileInfo from database'''

        sqlCommand = """SELECT  pf.file_name,
                                pf.file_type,
                                pf.file_checksum,
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
                                dfpa.relative_path,
                                pf.file_checksum_algorithm
                        FROM package_files AS pf
                             LEFT OUTER JOIN doc_file_package_associations AS dfpa ON pf.id = dfpa.package_file_id AND dfpa.package_id = %s 
                        WHERE pf.id = %s"""
        dbCursor.execute(sqlCommand, (package_id, package_file_id))
        queryResult = dbCursor.fetchone()

        if queryResult != None: 
            self.fileName = queryResult[0]
            self.fileType = queryResult[1]
            self.fileChecksum = queryResult[2]
            self.fileChecksumAlgorithm = queryResult[15]
            self.licenseConcluded = queryResult[3]
            self.licenseInfoInFile = queryResult[4].split()
            self.licenseComments = queryResult[5]
            self.fileCopyRightText = queryResult[6]
            self.artifactOfProjectName = queryResult[7]
            self.artifactOfProjectHomePage = queryResult[8]
            self.artifactOfProjectURI = queryResult[9]
            self.fileComment = queryResult[10]
            self.fileNotice = queryResult[11]
            self.fileContributor = queryResult[12]
            self.fileDependency = queryResult[13]
            self.fileRelativePath = queryResult[14]
            

    def insertFileInfo(self, spdx_doc_id, package_id, dbCursor):
        '''inserts fileInfo into database.'''

        '''Check if file is already in database'''
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

    def outputFileInfo_TAG(self):
        '''generates the file info in tag format'''
        output = ""
        output += "FileName: " + str(self.fileName) + '\n'

        if self.fileType != None:
            output += "FileType: "
            output += str(self.fileType) + '\n'

        output += "FileChecksum: " + str(self.fileChecksum) + '\n'
        output += "LicenseConcluded: " + str(self.licenseConcluded) + '\n'

        for license in self.licenseInfoInFile:
            output += "LicenseInfoInFile: " + str(license) + '\n'

        if self.licenseComments != None:
            output += "LicenseComments: <text>"
            output += str(self.licenseComments)
            output += "</text>\n"

        output += "FileCopyrightText: <text>"
        output += str(self.fileCopyRightText)
        output += "</text>\n"

        for projectName in self.artifactOfProjectName:
            output += "ArtifactOfProjectName: " + str(projectName) + '\n'

        for homePage in self.artifactOfProjectHomePage:
            output += "ArtifactOfProjectHomePage: " + str(homePage)

        for uri in self.artifactOfProjectURI:
            output += "ArtifactOfProjectURI: " + str(uri)

        if self.fileComment != None:
            output += "FileComment: <text>"
            output += str(self.fileComment)
            output += "</text>\n"

        if self.fileNotice != None:
            output += "FileNotice: <text>" + str(self.fileNotice) + "</text>"

        for contributor in self.fileContributor:
            output += "FileContributor: " + str(contributor)

        for dependency in self.fileDependency:
            output += "FileDependency: " + str(dependency)

        return output

    def outputFileInfo_RDF(self):
        output = ""
        output += '\t\t<fileName>' + str(self.fileName) + '</fileName>\n'

        if self.fileType != None:
            output += '\t\t<fileType rdf:resource="'
            output += str(self.fileType) + '"/>\n'

        output += '\t\t<checksum>\n'
        output += '\t\t\t<Checksum>\n'
        output += '\t\t\t\t<algorithm>'
        output += str(self.fileChecksumAlgorithm)
        output += '</algorithm>\n'
        output += '\t\t\t\t<checksumValue>'
        output += str(self.fileChecksum) + '</checksumValue>\n'
        output += '\t\t\t</Checksum>\n'
        output += '\t\t</checksum>\n'
        output += '\t\t<licenseConcluded>\n'
        output += '\t\t\t<DisjunctiveLicenseSet>\n'
        output += '\t\t\t\t<member rdf:resource="'
        output += str(self.licenseConcluded) + '"/>\n'
        output += '\t\t\t</DisjunctiveLicenseSet>\n'
        output += '\t\t</licenseConcluded>\n'

        for license in self.licenseInfoInFile:
            output += '\t\t<licenseInfoInFile rdf:resource="'
            output += str(license) + '/>\n'

        if self.licenseComments != None:
            output += '\t\t<licenseComments>'
            output += str(self.licenseComments)
            output += '</licenseComments>\n'

        output += '\t\t<copyrightText>'
        output += str(self.fileCopyRightText)
        output += '</copyrightText>\n'

        if len(self.artifactOfProjectName):
            output += '\t\t<artifactOf>\n'
            counter = 0
            for projectName in self.artifactOfProjectName:
                output += '\t\t\t<' + str(projectName) + ':Project>\n'
                output += '\t\t\t\t<doap:homepage rdf:resource="'
                output += str(self.artifactOfProjectHomePage[counter])
                output += '" />\n'
                output += '\t\t\t\t<artifactOf rdf:resource="'
                output += str(self.artifactOfProjectURI[counter]) + '" />\n'
                output += '\t\t\t</' + str(projectName) + ':Project>\n'
                counter = counter + 1
            output += '\t\t</artifactOf>\n'

        if self.fileComment != None:
            output += '\t\t<rdfs:comment>'
            output += str(self.fileComment)
            output += '</rdfs:comment>\n'

        if self.fileNotice != None:
            output += '\t\t<noticeText>'
            output += str(self.fileNotice)
            output += '</noticeText>\n'

        for contributor in self.fileContributor:
            output += '\t\t<fileContributor>'
            output += str(contributor)
            output += '</fileContributor>\n'

        for dependency in self.fileDependency:
            output += '\t\t<fileDependency rdf:nodeID="'
            output += str(dependency) + '"/>\n'

        return output
    
    def outputFileInfo_JSON(self):
        output = "{\n"
        output += '\t\t\t\t"fileName" : "' + str(self.fileName) + '",\n'
        output += '\t\t\t\t"fileType" : "' + str(self.fileType) + '",\n'
        output += '\t\t\t\t"checksum" : {\n'
        output += '\t\t\t\t\t"algorithm" : "' + str(self.fileChecksumAlgorithm) + '",\n'
        output += '\t\t\t\t\t"checksumValue" : "' + str(self.fileChecksum) + '"\n'
        output += '\t\t\t\t},\n'
        output += '\t\t\t\t"licenseConcluded" : "' + str(self.licenseConcluded) +'",\n'

        output += '\t\t\t\t"licenseInfoInFile" : [\n'
        count = 1
        for license in self.licenseInfoInFile:
            output += '\t\t\t\t\t"' + str(license) + '"'
            if count != len(self.licenseInfoInFile):
                output += ','
            output += '\n'
            count += 1
        output += '\t\t\t\t],\n'

        output += '\t\t\t\t"licenseComments": "' + str(self.licenseComments) + '",\n'
        output += '\t\t\t\t"copyrightText": "' + str(self.fileCopyRightText) + '",\n'

        output += '\t\t\t\t"artifactOf" : [\n'
        count = 1
        for projectName in self.artifactOfProjectName:
            output += '\t\t\t\t\t{\n'
            output += '\t\t\t\t\t\t"project" : "' + str(projectName) + '",\n'
            output += '\t\t\t\t\t\t"homepage" : "' + str(self.artifactOfProjectHomePage[count]) + '",\n'
            output += '\t\t\t\t\t\t"artifactOf" : "' + str(self.artifactOfProjectURI[counter]) +'"\n'
            output += '\t\t\t\t\t}'
            if count != len(self.artifactOfProjectName):
                output += ','
            output += '\n'
            count += 1
        output += '\t\t\t\t],\n'

        output += '\t\t\t\t"comment" : "' + str(self.fileComment) + '",\n' 
        output += '\t\t\t\t"noticeText" : "' + str(self.fileNotice) + '",\n'
        output += '\t\t\t\t"contributor" : "' + str(self.fileContributor) + '",\n'

        output += '\t\t\t\t"fileDependency" : [\n'
        count = 1
        for dependency in self.fileDependency:
            output += '\t\t\t\t\t"' + str(dependency) + '"'
            if count != len(self.fileDependency):
                output += ','
            output += '\n'
            count += 1
        output += '\t\t\t\t]\n'

        output += '\t\t\t}'
        
        return output

    def isCached(self):
        '''checks whether or not file is in database'''
        with MySQLdb.connect(host=settings.database_host,
                            user=settings.database_user,
                            passwd=settings.database_pass,
                            db=settings.database_name) as dbCursor:
            sqlCommand = """SELECT id
                            FROM package_files
                            WHERE file_checksum = %s"""
            dbCursor.execute(sqlCommand, (self.fileChecksum))
            queryResult = dbCursor.fetchone()

            if (queryResult == None):
                return -1
            else:
                return queryResult[0]

    def getChecksum(self):
        '''Generates the Sha1 checksum of a file'''
        with open(self.filePath, 'rb') as fileIn:
            self.fileChecksum = hashlib.sha1(fileIn.read()).hexdigest()

    def populateFileInfo(self,scanOption):
        '''Runs the two scanners and parses their output into the fileInfo object''' 

        ''' Get File Type'''
        mime = MimeTypes()
        self.fileType = mime.guess_type(self.filePath)[0]

        if self.fileType == None:
            self.fileType = 'Unknown'

        '''Check to see if file is cached.'''
        cached = self.isCached()

        '''If it isn't cached, run scans, else get file from database.'''
        if cached == -1:
           if (scanOption == 'fossology'):
            print "inside if condition";             
            '''Run fossology'''
            '''Fossology doesn't return an exit code of 0 so we must always catch the output.'''
            try:
                fossOutput = subprocess.check_output([settings.FOSSOLOGY_PATH,
                                                    self.filePath])
            except Exception as e:
                fossOutput = str(e.output)
            '''Parse outputs'''
            (fileName, fossLicense) = output_parser.foss_parser(fossOutput)
            self.licenseInfoInFile.append(fossLicense)
            self.licenseComments = "#FOSSology "
            self.licenseComments += fossLicense
           else:
            '''Scan to find licenses'''
            '''Run Ninka'''
            ninkaOutput = subprocess.check_output(
                                            [settings.NINKA_PATH, self.filePath],
                                    preexec_fn=lambda: signal(SIGPIPE, SIG_DFL)
                                )

            '''Run fossology'''
            '''Fossology doesn't return an exit code of 0 so we must always catch the output.'''
            try:
                fossOutput = subprocess.check_output([settings.FOSSOLOGY_PATH,
                                                    self.filePath])
            except Exception as e:
                fossOutput = str(e.output)

            '''Parse outputs'''
            (fileName, ninkaLicense) = output_parser.ninka_parser(ninkaOutput)
            (fileName, fossLicense) = output_parser.foss_parser(fossOutput)

            '''Get extracted text from ninka "senttok" file'''
            try:
                with open(self.filePath + ".senttok", 'r') as f:
                    for line in f:
                        if ninkaLicense in line:
                            line_tok = line.split(';')
                            self.extractedText +=  line_tok[3] + "\n"
                            self.extractedText +=  line_tok[4]
            except Exception as e:
                '''Do nothing, we just wont have extracted text for this license.'''

            '''License merging logic.'''
            fossLicense = fossLicense.upper().strip()
            ninkaLicense = ninkaLicense.upper().strip()
            match = output_parser.lic_compare(fossLicense, ninkaLicense)
            
            if match and fossLicense != 'ERROR':
                self.licenseInfoInFile.append(fossLicense)
            elif match and fossLicense == 'ERROR':
                self.licenseInfoInFile.append(ninkaLicense)
            elif not match and fossLicense == 'UNKNOWN':
                self.licenseInfoInFile.append(ninkaLicense)
            else:
                self.licenseInfoInFile.append("NO ASSERTION")

            self.licenseComments = "#FOSSology "
            self.licenseComments += fossLicense
            self.licenseComments += " #Ninka "
            self.licenseComments += ninkaLicense
        else:
            with MySQLdb.connect(host=settings.database_host,
                                user=settings.database_user,
                                passwd=settings.database_pass,
                                db=settings.database_name) as dbCursor:
                self.getFileInfo(cached, dbCursor)
