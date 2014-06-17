#!/usr/bin/python

'''
Defines the file level information in an spdx object.
'''
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
	
	def __init__(self, filePath = ""):
		self.filePath 				= filePath
		self.fileName 				= os.path.split(filePath)[1]
		self.fileType 				= ""
		self.fileChecksum 			= ""
		self.fileChecksumAlgorithm  		= "SHA1"
		self.licenseConcluded 			= "NO ASSERTION"
		self.licenseInfoInFile			= []
		self.licenseComments			= ""
		self.fileCopyRightText			= ""
		self.artifactOfProjectName		= ""
		self.artifactOfProjectHomePage		= ""
		self.artifactOfProjectURI 		= ""
		self.fileComment			= ""
		self.fileNotice				= ""
		self.fileContributor			= ""
		self.fileDependency			= ""
		self.fileRealativePath			= ""
		if self.filePath != "":
			self.getChecksum()	

	def getFileInfo(self, package_file_id, dbCursor):
		'''
		populates fileInfo from database
		'''
		sqlCommand = """SELECT file_name,
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
		self.fileName 			= queryResult[0]
		self.fileType 			= queryResult[1]
		self.fileChecksum 		= queryResult[2]
		self.fileChecksumAlgorithm	= queryResult[15]
		self.licenseConcluded 		= queryResult[3]
		self.licenseInfoInFile		= queryResult[4].split()
		self.licenseComments		= queryResult[5]
		self.fileCopyRightText		= queryResult[6]
		self.artifactOfProjectName	= queryResult[7]
		self.artifactOfProjectHomePage	= queryResult[8]
		self.artifactOfProjectURI 	= queryResult[9]
		self.fileComment		= queryResult[10]
		self.fileNotice			= queryResult[11]
		self.fileContributor		= queryResult[12]
		self.fileDependency		= queryResult[13]
		self.fileRealativePath		= queryResult[14]
	
	def insertFileInfo(self, spdx_doc_id, package_id):
		'''
		inserts fileInfo into database.
		'''
		with MySQLdb.connect(host = settings.database_host, user = settings.database_user, passwd = settings.database_pass, db = settings.database_name) as dbCursor:
			'''Get id of next file'''
			cached = self.isCached()
			
			fileId = cached
			if cached == -1:
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
								','.join(self.licenseInfoInFile), 
								self.fileChecksum, 
								self.fileChecksumAlgorithm, 
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
			
			for license in self.licenseInfoInFile:
				sqlCommand = """INSERT INTO package_license_info_from_files (package_id, package_license_info_from_files, created_at, updated_at)
						VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

				dbCursor.execute(sqlCommand, (package_id, license))
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
			print "LicenseInfoInFile: " + license
		
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
			
	def outputFileInfo_RDF(self):
		print '<fileName>' + self.fileName + '</fileName>'

		if self.fileType != "":
			print '<fileType rdf:resource="' + self.fileType + '"/>'

		print '<checksum>'
		print '<Checksum>'
		print '<algorithm>' + self.fileChecksumAlgorithm + '</algorithm>'
		print '<checksumValue>' + self.fileChecksum + '</checksumValue>'
		print '</Checksum>'
		print '</checksum>'
		print '<licenseConcluded>'
		print '<DisjunctiveLicenseSet>'
		print '<member rdf:resource="' + self.licenseConcluded + '"/>'
		print '</DisjunctiveLicenseSet>'
		print '</licenseConcluded>'

		for license in self.licenseInfoInFile:
			print '<licenseInfoInFile rdf:resource="' + license + '/>'
				
		if self.licenseComments != "":
 			print '<licenseComments>' + self.licenseComments + '</licenseComments>'
		
		print '<copyrightText>' + self.fileCopyRightText + '</copyrightText>'
		
		if len(self.artifactOfProjectName):
			print '<artifactOf>'
			counter = 0
			for projectName in self.artifactOfProjectName:
				print '<' + projectName + ':Project>'
				print '<doap:homepage rdf:resource="' + self.artifactOfProjectHomePage[counter] + '" />'
				print '<artifactOf rdf:resource="' + self.artifactOfProjectURI[counter] + '" />'		
				print '</' + projectName + ':Project>'
				counter = counter + 1
			print '</artifactOf>'
		if self.fileComment != "":
			print 	'<rdfs:comment>' + self.fileComment + '</rdfs:comment>'
		
		if self.fileNotice != "":
			print '<noticeText>' + self.fileNotice + '</noticeText>'
		
		for contributor in self.fileContributor:
                        print '<fileContributor>' + contributor + '</fileContributor>'
                for dependency in self.fileDependency:
                        print '<fileDependency rdf:nodeID="' + dependency + '"/>'

	def isCached(self):
		'''
		checks whether or not file is in database
		'''
		with MySQLdb.connect(host = settings.database_host, user = settings.database_user, passwd = settings.database_pass, db = settings.database_name) as dbCursor:
			sqlCommand = "SELECT id FROM package_files WHERE file_checksum = %s"
			dbCursor.execute(sqlCommand, (self.fileChecksum))
			queryResult = dbCursor.fetchone()

			if (queryResult == None):
				return -1
			else :
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
			ninkaOutput = subprocess.check_output([settings.NINKA_PATH, '-d', self.filePath], preexec_fn = lambda: signal(SIGPIPE, SIG_DFL))
			try:	
				fossOutput = subprocess.check_output([settings.FOSSOLOGY_PATH, self.filePath])
			except Exception as e:
				fossOutput = str(e.output)

			(fileName, fossLicense) = output_parser.ninka_parser(ninkaOutput)
			(fileName, ninkaLicense) = output_parser.foss_parser(fossOutput)

			fossLicense  = fossLicense.upper().strip()
			ninkaLicense = ninkaLicense.upper().strip()
			match        = output_parser.lic_compare(fossLicense, ninkaLicense)

			if match and fossLicense != 'ERROR':
				self.licenseInfoInFile.append(fossLicense)
			elif match and fossLicense == 'ERROR':
				self.licenseInfoInFile.append("NO ASSERTION")
			elif not match and fossLicense == 'UNKNOWN':
				self.licenseInfoInFile.append(ninkaLicense)
			else :
				self.licenseInfoInFile.append("NO ASSERTION")
				self.licenseComments  = "#FOSSology " + fossLicense + " #Ninka " + ninkaLicense 
 		else:
			self.getFileInfo(cached)

	
