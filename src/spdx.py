#!/user/bin/python

import creatorInfo
import packageInfo
import licensingInfo
import fileInfo
import reviewerInfo
import json
import MySQLdb

'''
This contains the definition for the SPDX object
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
		
	def insertSPDX(self, dbHost, dbUserName, dbUserPass, dbName):
		'''
		insert SPDX doc into db
		'''
		spdxDocId = None
		
        	with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
			
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
		creatorId = self.creatorInfo.insertCreatorInfo(spdxDocId, dbHost, dbUserName, dbUserPass, dbName)
		''' Insert Package Information '''
		packageId = self.packageInfo.insertPackageInfo(dbHost, dbUserName, dbUserPass, dbName)
		''' Insert File Information '''
		for files in self.fileInfo:
			files.insertFileInfo()
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

		print "## File Information\n"
		for files in self.fileInfo:
			files.outputFileInfo_TAG()
			print "\n"
		
		print "## License Information\n"
		for licenses in self.licensingInfo:
			licenses.outputLicensingInfo_TAG()
			print "\n"	
		
		print "## Reviewer Information\n"
		for reviewer in self.reviewerInfo:
			reviewer.outputReviewerInfo_TAG()
		
	def outputSPDX_JSON(self):
		print json.dumps(self)	
		
	def getSPDX(self, spdx_doc_id, dbHost, dbUsserName, dbUserPass, dbName):
		'''
		Generates the entire structure from the database.
		'''
		
	        with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:

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

	def getLicenseInfo(self, spdx_doc_id):
		'''
		Get the licenses of an spdx document from the database
		'''
		pass
	
	def getFileInfo(self, spdx_doc_id):
		'''
		Get the file info of an spdx document from the database
		'''
		pass

	def getReviewerInfo(self, spdx_doc_id):
		'''
		Get the reviewer info of an spdx document from the database
		'''
		pass

	def popluateFileInfo(self, path):
		'''
		Get the file info of an spdx document from the scanner
		'''
		
                

	
