#!/user/bin/python
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

'''Defines the package level information for the spdx object.'''
import MySQLdb
import settings
import os
import hashlib


class packageInfo:
    '''Initialize package object'''
    def __init__(self,
                 packagePath,
                 packageVersion=None,
                 packageSupplier=None,
                 packageOriginator=None,
                 packageDownloadLocation=None,
                 packageHomePage=None,
                 packageSourceInfo=None,
                 packageLicenseComments=None,
                 packageDescription=None):
        self.packagePath = packagePath
        self.packageName = None
        self.packageFileName = None
        self.packageVersion = packageVersion
        self.fileSize = None
        self.packageSupplier = packageSupplier
        self.packageOriginator = packageOriginator
        self.packageDownloadLocation = packageDownloadLocation
        self.packageVerificationCode = None
        self.packageChecksum = None
        self.packageChecksumAlgorithm = 'SHA1'
        self.packageHomePage = packageHomePage
        self.packageSourceInfo = packageSourceInfo
        self.packageLicenseConcluded = "NO ASSERTION"
        self.packageLicenseInfoFromFiles = []
        self.packageLicenseDeclared = "NO ASSERTION"
        self.packageLicenseComments = packageLicenseComments
        self.packageCopyrightText = ""
        self.packageSummary = ""
        self.packageDescription = packageDescription
        self.packageVerificationCodeExcludedFile = "None"

        '''If path is defined then run some of the procedures on it, 
        such as get checksum and package size.'''
        if packagePath != None:
            self.packageName = os.path.split(packagePath)[1]
            self.packageFileName = self.packageName
            self.getChecksum()
            self.fileSize = os.path.getsize(packagePath)

    def insertPackageInfo(self, dbCursor):
        '''inserts packageInformation into database.'''

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

    def outputPackageInfo_TAG(self):
        '''
        outputs package information to stdout
        if they are wrapped in an if statement they are optional params.
        '''
        output = ""
        output += "PackageName: " + str(self.packageName) + '\n'

        if self.packageVersion != None:
            output += "PackageVersion: " + str(self.packageVersion) + '\n'
        if self.packageFileName != None:
            output += "PackageFileName: " + str(self.packageFileName) + '\n'
        if self.packageSupplier != None:
            output += "PackageSupplier: " + str(self.packageSupplier) + '\n'
        if self.packageOriginator != None:
            output += "PackageOriginator: "
            output += str(self.packageOriginator) + '\n'

        output += "PackageDownloadLocation:    "
        output += str(self.packageDownloadLocation) + '\n'
        output += "PackageVerificationCode: "
        output += str(self.packageVerificationCode) + '\n'

        if self.packageChecksum != None:
            output += "PackageChecksum: " + str(self.packageChecksum) + '\n'
        if self.packageHomePage != None:
            output += "PackageHomePage: " + str(self.packageHomePage) + '\n'
        if self.packageSourceInfo != None:
            output += "PackageSourceInfo: "
            output += str(self.packageSourceInfo) + '\n'

        output += "PackageLicenseConcluded: "
        output += str(self.packageLicenseConcluded) + '\n'
        output += "PackageLicenseDeclared: "
        output += str(self.packageLicenseDeclared) + '\n'

        for license in self.packageLicenseInfoFromFiles:
            output += "PackageLicenseInfoFromFiles: " + str(license) + '\n'
        if self.packageLicenseComments != None:
            output += "PackageLicenseComments: <text>"
            output += str(self.packageLicenseComments) + "</text>\n"

        output += "PackageCopyrightText: <text>"
        output += str(self.packageCopyrightText) + "</text>\n"

        if self.packageSummary != None:
            output += "PackageSummary: <text>"
            output += str(self.packageSummary) + "</text>\n"
        if self.packageDescription != None:
            output += "PackageDescription: <text>"
            output += str(self.packageDescription) + "</text>\n"

        return output

    def outputPackageInfo_RDF(self):
        output = ""
        output += '\t\t<name>' + str(self.packageName) + '</name>\n'

        if self.packageVersion != None:
            output += '\t\t<versionInfo>'
            output += str(self.packageVersion)
            output += '</versionInfo>\n'
        if self.packageFileName != None:
            output += '\t\t<PackageFileName>'
            output += str(self.packageFileName)
            output += '</packageFileName>\n'
        if self.packageSupplier != None:
            output += '\t\t<supplier>'
            output += str(self.packageSupplier)
            output += '</supplier>\n'
        if self.packageOriginator != None:
            output += '\t\t<originator>'
            output += str(self.packageOriginator)
            output += '</originator>\n'

        output += '\t\t<downloadLocation>'
        output += str(self.packageDownloadLocation)
        output += '</downloadLocation>\n'
        output += '\t\t<packageVerificationCode>\n'
        output += '\t\t\t<PackageVerificationCode>\n'
        output += '\t\t\t<packageVerificationCodeValue>'
        output += str(self.packageVerificationCode)
        output += '</packageVerificationCodeValue>\n'
        output += '\t\t\t<packageVerificationCodeExcludedFile>'
        output += str(self.packageVerificationCodeExcludedFile)
        output += '</packageVerificationCodeExcludedFile>\n'
        output += '\t\t\t</PackageVerificationCode>\n'
        output += '\t\t</packageVerificationCode>\n'
        output += '\t\t<checksum>\n'
        output += '\t\t\t<Checksum>\n'
        output += '\t\t\t\t<algorithm rdf:resource="'
        output += str(self.packageChecksumAlgorithm) + '"/>\n'
        output += '\t\t\t\t<checksumValue>'
        output += str(self.packageChecksum)
        output += '</checksumValue>\n'
        output += '\t\t\t</Checksum>\n'
        output += '\t\t</checksum>\n'

        if self.packageHomePage != None:
            output += '\t\t<' + str(self.packageName)
            output += ':homepage rdf:resource="'
            output += str(self.packageHomePage) + '"/>\n'
        if self.packageSourceInfo != None:
            output += '\t\t<sourceInfo>'
            output += str(self.packageSourceInfo) + '</sourceInfo>\n'
        if self.packageLicenseConcluded != None:
            output += '\t\t<licenseConcluded>\n'
            output += '\t\t\t<DisjunctiveLicenseSet>\n'
            output += '\t\t\t\t<member rdf:resource="'
            output += str(self.packageLicenseConcluded) + '"/>\n'
            output += '\t\t\t</DisjunctiveLicenseSet>\n'
            output += '\t\t</licenseConcluded>\n'
        if self.packageLicenseDeclared != None:
            output += '\t\t<licenseDeclared>\n'
            output += '\t\t\t<ConjunctiveLicenseSet>\n'
            output += '\t\t\t\t<member rdf:resource="'
            output += str(self.packageLicenseDeclared) + '" />\n'
            output += '\t\t\t</ConjunctiveLicenseSet>\n'
            output += '\t\t</licenseDeclared>\n'

        for license in self.packageLicenseInfoFromFiles:
            output += '\t\t<licenseInfoFromFiles rdf:resource="'
            output += str(license) + '" />\n'

        if self.packageLicenseComments != None:
            output += '\t\t<licenseComments>'
            output += str(self.packageLicenseComments)
            output += '</licenseComments>\n'

        output += '\t\t<copyrightText>'
        output += str(self.packageCopyrightText)
        output += '</copyrightText>\n'

        if self.packageSummary != None:
            output += '\t\t<summary>'
            output += str(self.packageSummary)
            output += '</summary>\n'
        if self.packageDescription != None:
            output += '\t\t<description>'
            output += str(self.packageDescription)
            output += '</description>\n'

        return output

    def outputPackageInfo_JSON(self):
        output = "{\n"
        output += '\t\t\t"name" : "' + str(self.packageName) + '",\n'
        output += '\t\t\t"versioninfo" : "' + str(self.packageVersion) + '",\n'
        output += '\t\t\t"PackageFileName" : "' + str(self.packageFileName) + '",\n'
        output += '\t\t\t"supplier" : "' + str(self.packageSupplier) + '",\n'
        output += '\t\t\t"originator" : "' + str(self.packageOriginator) + '",\n'
        output += '\t\t\t"downloadLocation" : "' + str(self.packageDownloadLocation) + '",\n'

        output += '\t\t\t"packageVerificationCode" : {\n'
        output += '\t\t\t\t"pacakgeVerificationCodeValue" : "' + str(self.packageVerificationCode) + '",\n'
        output += '\t\t\t\t"packageVerificationCodeExcludedFile" : "' + str(self.packageVerificationCodeExcludedFile) + '"\n'
        output += '\t\t\t},\n'
        
        output += '\t\t\t"checksum" : {\n'
        output += '\t\t\t\t"algorithm" : "' + str(self.packageChecksumAlgorithm) + '",\n'
        output += '\t\t\t\t"checksumValue" : "' + str(self.packageChecksum) + '"\n'
        output += '\t\t\t},\n'

        output += '\t\t\t"homepage" : "' + str(self.packageHomePage) + '",\n'
        output += '\t\t\t"sourceInfo" : "' + str(self.packageSourceInfo) + '",\n'
        output += '\t\t\t"licenseConcluded" : "' + str(self.packageLicenseConcluded) + '",\n'
        output += '\t\t\t"licenseDeclared" : "' + str(self.packageLicenseDeclared) + '",\n'

        output += '\t\t\t"licenseInfoFromFiles" : [\n'
        count = 1
        for license in self.packageLicenseInfoFromFiles:
            output += '\t\t\t\t"' + str(license) + '"'
            if count != len(self.packageLicenseInfoFromFiles):
                output += ','
            output += '\n'
            count += 1
        output += '\t\t\t],\n'

        output += '\t\t\t"licenseComments" : "' + str(self.packageLicenseComments) + '",\n'
        output += '\t\t\t"copyrightText" : "' + str(self.packageCopyrightText) + '",\n'
        output += '\t\t\t"summary" : "' + str(self.packageSummary) + '",\n'
        output += '\t\t\t"description" : "' + str(self.packageDescription) + '"\n'
        output += '\t\t}\n'

        return output

    def getPackageInfo(self, package_id, dbCursor):
        '''gets package information from database'''

        sqlCommand = """SELECT package_name,
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
                           WHERE id = %s"""

        dbCursor.execute(sqlCommand, (package_id))
        queryReturn = dbCursor.fetchone()
        if queryReturn is not None:
            self.packageName = queryReturn[0]
            self.packageVersion = queryReturn[1]
            self.packageFileName = queryReturn[2]
            self.packageSupplier = queryReturn[3]
            self.packageOriginator = queryReturn[4]
            self.packageDownloadLocation = queryReturn[5]
            self.packageVerificationCode = queryReturn[6]
            self.packageChecksum = queryReturn[7]
            self.packageHomePage = queryReturn[8]
            self.packageSourceInfo = queryReturn[9]
            self.packageLicenseConcluded = queryReturn[10]
            self.packageLicenseDeclared = queryReturn[11]
            self.packageLicenseComments = queryReturn[12]
            self.packageCopyrightText = queryReturn[13]
            self.packageDescription = queryReturn[14]
            self.packageSummary = queryReturn[15]
            self.packageId = package_id

    def getChecksum(self):
        with open(self.packagePath, 'rb') as fileIn:
            self.packageChecksum = hashlib.sha1(fileIn.read()).hexdigest()

    def isCached(self):
        '''checks database to see if package is cached'''

        with MySQLdb.connect(host=settings.database_host,
                             user=settings.database_user,
                             passwd=settings.database_pass,
                             db=settings.database_name) as dbCursor:
            sqlCommand = "SELECT id FROM packages WHERE package_checksum = %s"
            dbCursor.execute(sqlCommand, (self.packageChecksum))

            queryReturn = dbCursor.fetchone()

            if (queryReturn == None):
                return -1
            else:
                return queryReturn[0]

    def generatePackageInfo(self, sha1List):
        '''Generate verification code'''
        sha1List.sort()
        self.packageVerificationCode = hashlib.sha1(
                                                    ''.join(sha1List)
                                                    ).hexdigest()

        cached = self.isCached()
        if cached != -1:
            with MySQLdb.connect(host=settings.database_host,
                                 user=settings.database_user,
                                 passwd=settings.database_pass,
                                 db=settings.database_name) as dbCursor:
                self.getPackageInfo(cached, dbCursor)
