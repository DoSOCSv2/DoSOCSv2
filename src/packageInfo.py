#!/user/bin/python

'''
Defines the package level information for the spdx object.
'''
import MySQLdb
import settings
import os
import hashlib

class packageInfo:
	
	def __init__(self, 
			packagePath, 
			packageVersion 		= "", 
			packageSupplier 	= "", 
			packageOriginator 	= "", 
			packageDownloadLocation = "", 
			packageHomePage 	= "", 
			packageSourceInfo 	= "", 
			packageLicenseComments 	= "", 
			packageDescription 	= ""):

		self.packagePath				= packagePath
		self.packageName 				= os.path.split(packagePath)[1]
		self.packageVersion 			 	= packageVersion
		self.packageFileName			 	= os.path.split(packagePath)[1]
		self.fileSize				 	= ""
		self.packageSupplier			 	= packageSupplier
		self.packageOriginator			 	= packageOriginator
		self.packageDownloadLocation			= packageDownloadLocation
		self.packageVerificationCode			= ""
		self.packageChecksum			 	= ""
		self.packageChecksumAlgorithm			= ""
		self.packageHomePage			 	= packageHomePage
		self.packageSourceInfo			 	= packageSourceInfo
		self.packageLicenseConcluded			= "NO ASSERTION"
		self.packageLicenseInfoFromFiles		= []
		self.packageLicenseDeclared		 	= "NO ASSERTION"
		self.packageLicenseComments		 	= packageLicenseComments
		self.packageCopyrightText		 	= ""
		self.packageSummary			 	= ""
		self.packageDescription			 	= packageDescription
		self.packageVerificationCodeExcludedFile 	= "None"
		if packagePath != "":
			self.getChecksum()
			self.fileSize = os.path.getsize(packagePath)
		
	def insertPackageInfo(self):
		'''
		inserts packageInformation into database.
		'''

		with MySQLdb.connect(host = settings.database_host, user = settings.database_user, passwd = settings.database_pass, db = settings.database_name) as dbCursor:
			sqlCommand = "SHOW TABLE STATUS LIKE 'packages'"
			dbCursor.execute(sqlCommand)
			packageId = dbCursor.fetchone()
			packageId = packageId[10]

			sqlCommand = """INSERT INTO packages (	package_name, 
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

					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

			dbCursor.execute( sqlCommand, 
							 (
								self.packageName, 
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
								self.packageVerificationCodeExcludedFile
							)
					)
		for license_info in self.packageLicenseInfoFromFiles:
			sqlCommand = """INSERT INTO package_license_info_from_files (package_id, package_license_info_from_files, created_at, updated_at)
				        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""
		
			dbCursor.execute( sqlCommand, 
						(
							packageId,
							license_info
						)
					)

		return packageId	
	
	def outputPackageInfo_TAG(self):
		'''
		outputs package information to stdout

		if they are wrapped in an if statement they are optional params.
		'''
		print "PackageName: " + self.packageName
		if self.packageVersion != "":
			print "PackageVersion: " + self.packageVersion
		if self.packageFileName != "":
			print "PackageFileName: " + self.packageFileName
		if self.packageSupplier != "":
			print "PackageSupplier: " + self.packageSupplier
		if self.packageOriginator != "":
			print "PackageOriginator: " + self.packageOriginator

		print "PackageDownloadLocation:	" + self.packageDownloadLocation
		print "PackageVerificationCode: " + self.packageVerificationCode
		
		if self.packageChecksum != "":
			print "PackageChecksum: " + self.packageChecksum
		if self.packageHomePage != "":
			print "PackageHomePage: " + self.packageHomePage
		if self.packageSourceInfo != "":
			print "PackageSourceInfo: " + self.packageSourceInfo

		print "PackageLicenseConcluded: " + self.packageLicenseConcluded
		print "PackageLicenseDeclared: " + self.packageLicenseDeclared

		for license in self.packageLicenseInfoFromFiles:
			print "PackageLicenseInfoFromFiles: " + license

		if self.packageLicenseComments != "":
			print "PackageLicenseComments: <text>" + self.packageLicenseComments + "</text>"

		print "PackageCopyrightText: <text>" + self.packageCopyrightText + "</text>"

		if self.packageSummary != "":
			print "PackageSummary: <text>" + self.packageSummary + "</text>"
		if self.packageDescription != "":
			print "PackageDescription: <text>" + self.packageDescription + "</text>"

	def outputPackageInfo_RDF(self):
		print '<name>' + self.packageName + '</name>'
		if self.packageVersion != "":
                        print '<versionInfo>' + self.packageVersion + '</versionInfo>'
                if self.packageFileName != "":
                        print '<PackageFileName>' + self.packageFileName + '</packageFileName>'
                if self.packageSupplier != "":
                        print '<supplier>' + self.packageSupplier + '</supplier>'
                if self.packageOriginator != "":
                        print '<originator>' + self.packageOriginator + '</originator>'

                print '<downloadLocation>' + self.packageDownloadLocation + '</downloadLocation>'
		print '<packageVerificationCode>'
		print '<PackageVerificationCode>'
		print '<packageVerificationCodeValue>' + self.packageVerificationCode + '</packageVerificationCodeValue>'
		print '<packageVerificationCodeExcludedFile>' + self.packageVerificationCodeExcludedFile +  '</packageVerificationCodeExcludedFile>'
		print '</PackageVerificationCode>'
		print '</packageVerificationCode>'
		print '<checksum>'
		print '<Checksum>'
		print '<algorithm rdf:resource="' + self.packageChecksumAlgorithm + '"/>'
		print '<checksumValue>' + self.packageChecksum + '</checksumValue>'
		print '</Checksum>'
		print '</checksum>'
		

                if self.packageHomePage != "":
                        print '<' + self.packageName + ':homepage rdf:resource="' + self.packageHomePage + '"/>'
                if self.packageSourceInfo != "":
                        print '<sourceInfo>' + self.packageSourceInfo + '</sourceInfo>'

		if self.packageLicenseConcluded  != "":
	                print '<licenseConcluded>'
			print '<DisjunctiveLicenseSet>'
			print '<member rdf:resource="' + self.packageLicenseConcluded + '"/>'
			print '</DisjunctiveLicenseSet>'

		if self.packageLicenseDeclared != "":
			print '<licenseDeclared>'
			print '<ConjunctiveLicenseSet>'
			print '<member rdf:resource="' + self.packageLicenseDeclared + '" />'
			print '</ConjunctiveLicenseSet>'
			print '</licenseDeclared>'

                for license in self.packageLicenseInfoFromFiles:
                        print '<licenseInfoFromFiles rdf:resource="' + license + '" />'

                if self.packageLicenseComments != "":
                        print '<licenseComments>' + self.packageLicenseComments + '</licenseComments>'

                print '<copyrightText>' + self.packageCopyrightText + '</copyrightText>'

                if self.packageSummary != "":
                        print '<summary>' + self.packageSummary + '</summary>'
                if self.packageDescription != "":
                        print '<description>' + self.packageDescription + '</description>'
		
	def getPackageInfo(self, package_id, dbCursor):
		'''
		gets package information from database
		'''
		
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
			
		self.packageName 			= queryReturn[0]
		self.packageVersion 			= queryReturn[1]
		self.packageFileName			= queryReturn[2]
		self.packageSupplier			= queryReturn[3]
		self.packageOriginator			= queryReturn[4]
		self.packageDownloadLocation		= queryReturn[5]
		self.packageVerificationCode		= queryReturn[6]
		self.packageChecksum			= queryReturn[7]
		self.packageHomePage			= queryReturn[8]
		self.packageSourceInfo			= queryReturn[9]
		self.packageLicenseConcluded		= queryReturn[10]
		self.packageLicenseDeclared		= queryReturn[11]
		self.packageLicenseComments		= queryReturn[12]
		self.packageCopyrightText		= queryReturn[13]
		self.packageDescription			= queryReturn[14]
		self.packageSummary			= queryReturn[15]

	def getChecksum(self):
                with open(self.packagePath, 'rb') as fileIn:
                        self.packageChecksum = hashlib.sha1(fileIn.read()).hexdigest()

	def isCached(self):
		'''
		checks database to see if package is cached
		'''

		with MySQLdb.connect(host = settings.database_host, user = settings.database_user, passwd = settings.database_pass, db = settings.database_name) as dbCursor:
			sqlCommand = "SELECT id FROM packages WHERE package_checksum = %s"
			dbCursor.execute(sqlCommand, (self.packageChecksum))

			queryReturn = dbCursor.fetchone()

			if (queryReturn == None):
				return -1
			else :
				return queryReturn[0]
	
	def generatePackageInfo(self, sha1List):
		'''Generate verification code'''
		sha1List.sort()
		self.packageVerificationCode = hashlib.sha1(''.join(sha1List)).hexdigest()
		
		cached = self.isCached()
		if cached != -1:
			self.getPackageInformation(cached)

