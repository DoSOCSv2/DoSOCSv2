#!/usr/bin/python
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
    def __init__(self, filePath=None, fileRealativePath = ""):
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
        self.fileRealativePath = fileRealativePath

        if self.filePath != None:
            self.getChecksum()
            self.fileName = os.path.split(filePath)[1]

    def getFileInfo(self, package_file_id, dbCursor):
        '''populates fileInfo from database'''

        sqlCommand = """SELECT  file_name,
                                file_type,
                                file_checksum,
                                license_concluded,
                                license_info_in_file,
                                license_comments,
                                file_copyright_text,
                                artifact_of_project_name,
                                artifact_of_project_homepage,
                                artifact_of_project_uri,
                                file_comment,
                                file_notice,
                                file_contributor,
                                file_dependency,
                                relative_path,
                                file_checksum_algorithm
                        FROM package_files WHERE id = %s"""
        dbCursor.execute(sqlCommand, package_file_id)
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
            self.fileRealativePath = queryResult[14]

    def insertFileInfo(self, spdx_doc_id, package_id, dbCursor):
        '''inserts fileInfo into database.'''
        '''Get id of next file'''
        fileId = self.isCached()

        if fileId == -1:
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
                                    relative_path,
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
                                        self.fileRealativePath,
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
                                    created_at,
                                    updated_at)
                        VALUES (%s,
                                %s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        dbCursor.execute(sqlCommand, (spdx_doc_id, package_id, fileId))

        sqlCommand = """INSERT INTO package_license_info_from_files
                                        (package_id,
                                        package_license_info_from_files,
                                        created_at,
                                        updated_at)
                        VALUES (%s,
                                %s,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP)"""

        for license in self.licenseInfoInFile:
            dbCursor.execute(sqlCommand, (package_id, license))

        return fileId

    def outputFileInfo_TAG(self):
        '''outputs fileInfo to stdout'''
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
        with open(self.filePath, 'rb') as fileIn:
            self.fileChecksum = hashlib.sha1(fileIn.read()).hexdigest()

    def populateFileInfo(self):
        ''' Get File Type'''
        mime = MimeTypes()
        self.fileType = mime.guess_type(self.filePath)[0]

        if self.fileType == None:
            self.fileType = 'Unknown'

        cached = self.isCached()

        if cached == -1:
            '''Scan to find licenses'''
            ninkaOutput = subprocess.check_output(
                                            [settings.NINKA_PATH,
                                            '-d', self.filePath],
                                    preexec_fn=lambda: signal(SIGPIPE, SIG_DFL)
                                )
            try:
                fossOutput = subprocess.check_output([settings.FOSSOLOGY_PATH,
                                                    self.filePath])
            except Exception as e:
                fossOutput = str(e.output)

            (fileName, fossLicense) = output_parser.ninka_parser(ninkaOutput)
            (fileName, ninkaLicense) = output_parser.foss_parser(fossOutput)

            fossLicense = fossLicense.upper().strip()
            ninkaLicense = ninkaLicense.upper().strip()
            match = output_parser.lic_compare(fossLicense, ninkaLicense)

            if match and fossLicense != 'ERROR':
                self.licenseInfoInFile.append(fossLicense)
            elif match and fossLicense == 'ERROR':
                self.licenseInfoInFile.append("NO ASSERTION")
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
