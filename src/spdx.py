#!/user/bin/python

import errno
import creatorInfo
import packageInfo
import licensingInfo
import fileInfo
import reviewerInfo
import os
import json
import MySQLdb
import tempfile
import shutil
import settings
import tarfile
import zipfile
import sets

'''
This contains the definition for the SPDX object.
'''

class SPDX:
	def __init__(	self, 
			packagePath,
			version 			= "1.2", 
			dataLicense 			= "CC-1.0", 
			documentComment 		= "", 
			creator 			= "", 
			creatorComment 			= "", 
			licenseListVersion 		= "",
			packageVersion 			= "", 
			packageSupplier 		= "", 
			packageOriginator 		= "", 
			packageDownloadLocation 	= "", 
			packageHomePage 		= "", 
			packageSourceInfo 		= "", 
			packageLicenseComments 		= "", 
			packageDescription 		= ""):

		self.packagePath		= packagePath
		self.version 			= version
		self.dataLicense 		= dataLicense
		self.documentComment 		= documentComment
		self.creatorInfo		= creatorInfo.creatorInfo(creator, creatorComment, licenseListVersion)
		self.packageInfo		= packageInfo.packageInfo(	packagePath,
										packageVersion, 
										packageSupplier, 
										packageOriginator, 
										packageDownloadLocation, 
										packageHomePage, 
										packageSourceInfo, 
										packageLicenseComments, 
										packageDescription)
		self.licensingInfo		= []
		self.fileInfo			= []
		self.reviewerInfo		= []
		
	def insertSPDX(self):
		'''
		insert SPDX doc into db
		'''
		spdxDocId = None
		
        	with MySQLdb.connect(host = settings.database_host, user = settings.database_user, passwd = settings.database_pass, db = settings.database_name) as dbCursor:
			
			'''get spdx doc id'''
			sqlCommand = "SHOW TABLE STATUS LIKE 'spdx_docs'"
			dbCursor.execute(sqlCommand)
			spdxDocId = dbCursor.fetchone()[10]

			'''Insert spdx info'''
			sqlCommand = 	"""INSERT INTO spdx_docs (spdx_version,
					 			  data_license, 
								  upload_file_name, 
								  upload_content_type, 
								  upload_file_size, 
								  upload_updated_at, 
								  document_comment, 
								  created_at, 
								  updated_at) 
						   VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

			dbCursor.execute(sqlCommand, (self.version, self.dataLicense, self.packageInfo.packageName, 'SQL', self.packageInfo.fileSize, self.documentComment))
			
		''' Insert Creator Information '''
		creatorId = self.creatorInfo.insertCreatorInfo(spdxDocId)
		''' Insert Package Information '''
		packageId = self.packageInfo.insertPackageInfo()
		''' Insert File Information '''
		for files in self.fileInfo:
			files.insertFileInfo(spdxDocId, packageId)
		''' Insert License Information '''
		for licenses in self.licensingInfo:
			licenses.insertLicensingInfo(spdxDocId)
		''' Insert Reviewer Information '''
		for reviewer in self.reviewerInfo:
			reviewer.insertReviewerInfo(spdxDocId)

	def outputSPDX_TAG(self):
		
		'''
		output SPDX doc to stdout
		'''
		print "SPDXVersion: " + self.version
		print "DataLicense: " + self.dataLicense
		print "Document Comment: <text>" + self.documentComment + "</text>"
		print "\n"
		
		print "## Creation Information\n"
		self.creatorInfo.outputCreatorInfo_TAG()
		print "\n"
	
		print "## Package Information\n"
		self.packageInfo.outputPackageInfo_TAG()
		print "\n"

		print "## File Information\n"
		for files in self.fileInfo:
			files.outputFileInfo_TAG()
			print "\n"
		
		print "## License Information\n"
		for licenses in self.licensingInfo:
			licenses.outputLicensingInfo_TAG()
			print "\n"	
		
		if len(self.reviewerInfo) > 0:
			print "## Reviewer Information\n"
			for reviewer in self.reviewerInfo:
				reviewer.outputReviewerInfo_TAG()

	def outputSPDX_RDF(self):
		print '<SpdxDocument rdf:about="">'
		print '<specVersion>' + self.version + '</specVersion>'
		print '<dataLicense rdf:resource="' + self.dataLicense + '" />'
		print '<rdfs:comment>' + self.documentComment + '</rdfs:comment>'

		print '<CreationInfo>'
		self.creatorInfo.outputCreatorInfo_RDF()
		print '</CreationInfo>'

		print '<Package rdf:about="">'
		self.packageInfo.outputPackageInfo_RDF()
		print '</Package>'

		for files in self.fileInfo:
			print '<File rdf:about="">'
			files.outputFileInfo_RDF()
			print '</File>'
				
		if len(self.licensingInfo) > 0:
			for licenses in self.licensingInfo:
				print '<ExtractedLicensingInfo>'
				licenses.outputLicensingInfo_RDF()
				print '</ExtractedLicensingInfo>'

		print '</SpdxDocument>'		

	def outputSPDX_JSON(self):
		print json.dumps(self)	
		
	def getSPDX(self, spdx_doc_id):
		'''
		Generates the entire structure from the database.
		'''
		
	        with MySQLdb.connect(host = settings.database_host, user = settings.database_user, passwd = settings.database_pass, db = settings.database_name) as dbCursor:

			sqlCommand = """SELECT spdx_version,data_license,document_comment FROM spdx_docs WHERE spdx_doc_id = ?"""
			dbCursor.execute(sqlCommand, spdx_doc_id)
			rows = dbCursor.fetchone()
			if rows:
				self.version = rows.spdx_version
				self.dataLicense = rows.data_license
				self.documentComment = rows.document_comment

			self.creatorInfo.getCreatorInfo(spdx_doc_id)
			self.packageInfo.getPackageInfo(spdx_doc_id)
			self.licensingInfo = getLicenseInfo(spdx_doc_id)
			self.fileInfo = getFileInfo(spdx_doc_id)
			self.reviewInfo = getReviewerInfo(spdx_doc_id)

	def generateSPDXDoc(self):
		'''
		Generates the entire structure by querying and scanning the files.
		'''
		extractTo 		= tempfile.mkdtemp()
		ninka_out 		= tempfile.NamedTemporaryFile() 
		foss_out 		= tempfile.NamedTemporaryFile()
		licenseCounter 		= 0
		scanners 		= []
		licensesFromFiles 	= []
		sha1Checksums		= []

		if tarfile.is_tarfile(self.packagePath):
			archive = tarfile.open(self.packagePath)
			archive.extractall(extractTo)				
			for fileName in archive.getnames():
				if os.path.isfile(os.path.join(extractTo, fileName)):
					tempFileInfo = fileInfo.fileInfo(os.path.join(extractTo, fileName))
					tempFileInfo.populateFileInfo()
					tempLicenseInfo = licensingInfo.licensingInfo("LicenseRef-" + str(licenseCounter), "", tempFileInfo.licenseInfoInFile[0], "", tempFileInfo.licenseComments)
					if tempLicenseInfo not in self.licensingInfo:
						self.packageInfo.packageLicenseInfoFromFiles.append(tempLicenseInfo.licenseId)
						self.licensingInfo.append(tempLicenseInfo)
						licenseCounter += 1

					sha1Checksums.append(tempFileInfo.fileChecksum)
					self.fileInfo.append(tempFileInfo)
											
		elif zipfile.is_zipfile(self.packagePath):
			'''TODO
			archive = zipfile.ZipFile(self.packagePath, "r")
			archive.extractall(extractTo)
			names = archive.namelist()
			'''
		self.packageInfo.generatePackageInfo(sha1Checksums)
		ninka_out.close()
		foss_out.close()
