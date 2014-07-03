#!/usr/bin/python

'''
Defines the license level information in the spdx object.
'''
import MySQLdb
import settings

class licensingInfo:
	
	def __init__(self, licenseId = None, extractedText = None, licenseName = None, licenseCrossReference = None, licenseComment = None, fileChecksum = None):
		self.licenseId 				= licenseId
		self.extractedText 			= extractedText
		self.licenseName			= licenseName
		self.licenseCrossReference 	= licenseCrossReference
		self.licenseComment			= licenseComment
		self.fileChecksum			= fileChecksum
	
	def insertLicensingInfo(self, spdx_doc_id, dbCursor, osi_approved = "", standard_license_header = ""):
		'''
		inserts licensingInfo into database
		'''
		'''Get File Id'''
		sqlCommand = """SELECT id FROM package_files WHERE file_checksum = %s"""
		dbCursor.execute(sqlCommand, (self.fileChecksum))
		package_file_id = dbCursor.fetchone()[0]
		
		'''Get id of license'''
		sqlCommand = """SHOW TABLE STATUS LIKE 'licenses'"""
		dbCursor.execute(sqlCommand)
		licenseId = dbCursor.fetchone()[10]

		sqlCommand = """INSERT INTO licenses (extracted_text, license_name, osi_approved, standard_license_header, license_cross_reference, created_at, updated_at)
			        	VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

		dbCursor.execute(sqlCommand, (self.extractedText, self.licenseName, osi_approved, standard_license_header, self.licenseCrossReference))
		
		'''Get doc_license_association_id'''

		sqlCommand = """SHOW TABLE STATUS LIKE 'doc_license_associations'"""
		dbCursor.execute(sqlCommand)
		docLicenseAssoc = dbCursor.fetchone()[10]

		sqlCommand = """INSERT INTO doc_license_associations (spdx_doc_id, license_id, license_identifier, license_name, license_comments, created_at, updated_at)
			        	VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

		dbCursor.execute(sqlCommand, (spdx_doc_id, licenseId, self.licenseId, self.licenseName, self.licenseComment))
		
		sqlCommand = """INSERT INTO licensings (package_file_id, juncture, doc_license_association_id, created_at, updated_at)
						VALUES (%s, "", %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""
		
		dbCursor.execute(sqlCommand, (package_file_id, docLicenseAssoc))

		return licenseId

	def outputLicensingInfo_TAG(self):
		'''
		outputs licensingInfo to stdout
		'''
		
		output = ""
		output += "LicenseID: " + str(self.licenseId) + '\n'
		output += "LicenseName: " + str(self.licenseName) + '\n'
	
		if self.licenseCrossReference != None:
			for reference in self.licenseCrossReference:
				output += "LicenseCrossReference: " + str(reference) + '\n'

		output += "ExtractedText: <text>" + str(self.extractedText) + "</text>\n"
		
		if self.licenseComment != "":
			output += "LicenseComment: <text>" + str(self.licenseComment) + "</text>\n"
			
		return output
		
	def outputLicensingInfo_RDF(self):
		output = ""
		output += '\t\t<licenseId>' + str(self.licenseId) + '</licenseId>\n'
		output += '\t\t<licenseName>' + str(self.licenseName) + '</licenseName>\n'
		output += '\t\t<extractedText>' + str(self.extractedText) + '</extractedText>\n'
		if self.licenseCrossReference != None:
			for reference in self.licenseCrossReference:
				output += '\t\t<rdfs:seeAlso>' + str(self.reference) + '</rdfs:seeAlso>\n'

		if self.licenseComment != None:
			output += '\t\t<rdfs:comment>' + str(self.licenseComment) + '</rdfs:comment>\n'
		
		return output
	
	def getLicensingInfo(self, doc_license_association_id, dbCursor):
		'''
		populates licensingInfo from database
		'''
		sqlCommand = """SELECT	dla.license_identifier,
								dla.license_name,
								dla.license_comments,
								l.extracted_text,
								l.license_cross_reference
	
						FROM doc_license_associations AS dla
						     INNER JOIN licenses AS l ON dla.license_id = l.id
		
						WHERE dla.id = %s"""
		dbCursor.execute(sqlCommand, (doc_license_association_id))
	
		queryReturn = dbCursor.fetchone()
		if queryReturn is not None:
			self.licenseId 				= queryReturn[0]
			self.licenseName 			= queryReturn[1]
			self.licenseComment 		= queryReturn[2]
			self.extractedText 			= queryReturn[3]
			self.licenseCrossReference 	= queryReturn[4]
