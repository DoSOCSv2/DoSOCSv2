#!/usr/bin/python

'''
Defines the file level information in an spdx object.
'''
import checksum
import MySQLdb

class fileInfo:
	
	def __init__(self, filePath):
		self.fileName 				= ""
		self.fileType 				= ""
		self.fileChecksum 			= ""
		self.licenseConcluded 			= ""
		self.licenseInfoInFile			= ""
		self.licenseComments			= ""
		self.fileCopyRightText			= ""
		self.artifactOfProjectName		= ""
		self.artifactOfProjectHomePage		= ""
		self.artifactOfProjectURI 		= ""
		self.fileComment			= ""
		self.fileNotice				= ""
		self.fileContributor			= ""
		self.fileDependency			= ""
		self.fileRealativePath			= filePath
		

	def getFileInfo(self, package_file_id, dbHost, dbUsserName, dbUserPass, dbName):
		'''
		populates fileInfo from database
		'''

		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:

			sqlCommand = """SELECT * FROM package_files WHERE id = ?"""
			dbCursor.execute(sqlCommand, package_file_id)
			queryResult = dbCursor.fetchone()

			self.fileName 			= queryResult.file_name
			self.fileType 			= queryResult.file_type
			self.fileChecksum 		= queryResult.file_checksum
			self.licenseConcluded 		= queryResult.license_concluded
			self.licenseInfoInFile		= queryResult.license_info_in_file
			self.licenseComments		= queryResult.license_comments
			self.fileCopyRightText		= queryResult.file_copyright_text
			self.artifactOfProjectName	= queryResult.artifact_of_project_name
			self.artifactOfProjectHomePage	= queryResult.artifact_of_project_homepage
			self.artifactOfProjectURI 	= queryResult.artifact_of_project_uri
			self.fileComment		= queryResult.file_comment
			self.fileNotice			= queryResult.file_notice
			self.fileContributor		= queryResult.file_contributor
			self.fileDependency		= queryResult.file_dependency
			self.fileRealativePath		= queryResult.relative_path
	
	def insertFileInfo(self, spdx_doc_id, package_id, dbHost, dbUserName, dbUserPass, dbName, file_checksum_algorithm = "SHA1"):
		'''
		inserts fileInfo into database.
		'''
		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
			'''Get id of next file'''
			sqlCommand = "SHOW TABLE STATUS LIKE 'package_files'"
			dbCursor.execute(sqlCommand)
			fileId = dbCursor.fetchone()[10]


			sqlCommand = """INSERT INTO package_files (file_name, 
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
					  	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""
	
			dbCursor.execute( sqlCommand, 
					       	(
							self.fileName, 
							self.fileType, 
							self.fileCopyRightText, 
							self.artifactOfProjectName, 
							self.artifactOfProjectHomePage, 
							self.artifactOfProjectURI, 
							self.licenseConcluded, 
							self.licenseInfoInFile, 
							self.fileChecksum, 
							file_checksum_algorithm, 
							self.fileRealativePath, 
							self.licenseComments, 
							self.fileNotice, 
							self.fileContributor, 
							self.fileDependency, 
							self.fileComment
						)
					)
	
			sqlCommand = """INSERT INTO doc_file_package_associations (spdx_doc_id, package_id, package_file_id, created_at, updated_at)
  				        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

			dbCursor.execute(sqlCommand, (spdx_doc_id, package_id, fileId))

		return fileId

	def outputFileInfo_TAG(self):
		'''
		outputs fileInfo to stdout
		'''
		print "FileName: " + self.fileName
		
		if self.fileType != "":
			print "FileType: " + self.fileType
		
		print "FileChecksum: " + self.fileChecksum
		print "LicenseConcluded: " + self.licenseConcluded
		
		for license in self.licenseInfoInFile:
			print "LicenseInfoInFile: " + self.licenseInfoInFile
		
		if self.licenseComments != "":
			print "LicenseComments: <text>" + self.licenseComments + "</text>"
		
		print "FileCopyrightText: <text>" + self.fileCopyRightText + "</text>"
				
		for projectName in self.artifactOfProjectName:
			print "ArtifactOfProjectName: " + projectName
		for homePage in self.artifactOfProjectHomePage:
			print "ArtifactOfProjectHomePage: " + homePage
		for uri in self.artifactOfProjectURI:
			print "ArtifactOfProjectURI: " + uri

		if self.fileComment != "":
			print "FileComment: <text>" + self.fileComment + "</text>"
		if self.fileNotice != "":
			print "FileNotice: <text>" + self.fileNotice + "</text>"

		for contributor in self.fileContributor:
			print "FileContributor: " + contributor
		for dependency in self.fileDependency:
			print "FileDependency: " + dependency		
			
 
	def isCached(self, file_checksum, dbHost, dbUsserName, dbUserPass, dbName):
		'''
		checks whether or not file is in database
		'''
		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
			sqlCommand = "SELECT id FROM package_files WHERE file_checksum = %s"
			dbCursor.execute(sqlCommand, (file_checksum))
			queryResult = dbCursor.fetchone()

			if (queryResult == None):
				return -1
			else :
				return queryResult.id

	def getFileInfo(self):
		self.fileChecksum = checksum.getChecksum(self.filePath)
