#!/user/bin/python

import MySQLdb
import checksum 

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

		self.packageName 				= ""
		self.packageVersion 			 	= packageVersion
		self.packageFileName			 	= ""
		self.fileSize				 	= 100
		self.packageSupplier			 	= packageSupplier
		self.packageOriginator			 	= packageOriginator
		self.packageDownloadLocation			= packageDownloadLocation
		self.packageVerificationCode			= ""
		self.packageChecksum			 	= "" #checksum(packagePath)
		self.packageHomePage			 	= packageHomePage
		self.packageSourceInfo			 	= packageSourceInfo
		self.packageLicenseConcluded			= ""
		self.packageLicenseInfoFromFiles		= ""
		self.packageLicenseDeclared		 	= ""
		self.packageLicenseComments		 	= packageLicenseComments
		self.packageCopyrightText		 	= ""
		self.packageSummary			 	= ""
		self.packageDescription			 	= packageDescription
		self.packageVerficationCodeExcludedFile 	= ""
		
	def insertPackageInfo(self, dbHost, dbUserName, dbUserPass, dbName, checksum_algorithm = "SHA1"):
		'''
		inserts packageInformation into database.
		'''

		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
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
								package_license_info_from_files, 
								package_license_comments,
								package_verification_code, 
								package_verification_code_excluded_file, 
								created_at, 
								updated_at)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

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
								checksum_algorithm, 
								self.packageHomePage, 
								self.packageSourceInfo, 
								self.packageLicenseInfoFromFiles, 
								self.packageLicenseComments, 
								self.packageVerificationCode, 
								self.packageVerficationCodeExcludedFile
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
			print "PackageLicenseInfoFromFiles: " + license.name

		if self.packageLicenseComments != "":
			print "PackageLicenseComments: <text>" + self.packageLicenseComments + "</text>"

		print "PackageCopyrightText: <text>" + self.packageCopyrightText + "</text>"

		if self.packageSummary != "":
			print "PackageSummary: <text>" + self.packageSummary + "</text>"
		if self.packageDescription != "":
			print "PackageDescription: <text>" + self.packageDescription + "</text>"

		
	def getPackageInformation(self, package_id, dbHost, dbUserName, dbUserPass, dbName):
		'''
		gets package information from database
		'''
		
		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
			sqlCommand = "SELECT * FROM packages WHERE id = ?"
			dbCursor.execute(sqlCommand, (package_id))	
			queryReturn = dbCursor.fetchone()

			self.packageName 			= queryReturn.package_name
			self.packageVersion 			= queryReturn.package_version
			self.packageFileName			= queryReturn.package_file_name
			self.packageSupplier			= queryReturn.package_supplier
			self.packageOriginator			= queryReturn.package_originator
			self.packageDownloadLocation		= queryReturn.package_download_location
			self.packageVerificationCode		= queryReturn.verification_code
			self.packageChecksum			= queryReturn.package_checksum
			self.packageHomePage			= queryReturn.package_home_page
			self.packageSourceInfo			= queryReturn.package_source_info
			self.packageLicenseConcluded		= queryReturn.package_license_concluded
			self.packageLicenseInfoFromFiles	= queryReturn.package_license_info_from_files
			self.packageLicenseDeclared		= queryReturn.package_license_declared
			self.packageLicenseComments		= queryReturn.package_license_comments
			self.packageCopyrightText		= queryReturn.package_copyright_text
			self.packageDescription			= queryReturn.package_description
			self.packageSummary			= queryReturn.package_summary

	def isCached(self, package_checksum, dbHost, dbUsserName, dbUserPass, dbName):
		'''
		checks database to see if package is cached
		'''

		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
			sqlCommand = "SELECT id FROM packages WHERE package_checksum = ?"
			dbCursor.execute(sqlCommand, (package_checksum))

			queryReturn = dbCursor.fetchone()

			if (queryReturn == None):
				return -1
			else :
				return queryReturn.id
