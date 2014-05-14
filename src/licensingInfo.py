#!/usr/bin/python

import MySQLdb
import ConfigParser

class licensingInfo:
	
	def __init__(self):
		self.licenseId 			= ""
		self.extractedText 		= ""
		self.licenseName		= ""
		self.licenseCrossReference 	= []	
		self.licenseComment		= ""
	
	def insertLicensingInfo(self, spdx_doc_id, osi_approved = "", standard_license_header = ""):
		'''
		inserts licensingInfo into database
		'''

		'''Create connection'''
		with ConfigParser.ConfigParser() as configParser:
			configParser.read("do_spdx.cfg")
			dbUserName   = configParser.get('Database','database_user')
			dbUserPass   = configParser.get('Database','database_pass')
			dbHost       = configParser.get('Database','database_host')
			dbName       = configParser.get('Database','database_name')

		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
			'''Get id of license'''
			sqlCommand = "SHOW TABLE STATUS LIKE 'licenses'"
			dbCursor.execute(sqlCommand)
			licenseId = dbCursor.fetchone()
			licenseId = licenseId['Auto_increment']
	
			sqlCommend = """INSERT INTO licenses (extracted_text, license_name, osi_approved, standard_license_header, license_cross_reference, created_at, updated_at)
				        VALUES (?, ?, ?, ?, ?, CURRNET_TIMESTAMP, CURRENT_TIMESTAMP)"""

			dbCursor.execute(sqlCommand, (self.extractedText, self.licenseName, osi_approved, standard_license_header, self.licenseCrossReference))

			sqlCommand = """INSERT INTO doc_license_associations (spdx_doc_id, license_id, license_identifier, license_name, license_comments, created_at, updated_at)
				        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""

			dbCursor.execute(sqlCommand, spdx_doc_id, licenseId, self.licenseId, self.licenseName, self.licenseComment)

		return licenseId

	def outputLicensingInfo_TAG(self):
		'''
		outputs licensingInfo to stdout
		'''
		print "LicenseID: " + self.licenseId
		print "LicenseName: " + self.licenseName
	
		for reference in self.licenseCrossReference:
			print "LicenseCrossReference: " + reference

		print "ExtractedText: <text>" + self.extractedText + "</text>"
		if self.licenseComment != "":
			print "LicenseComment: <text>" + self.licenseComment + "</text>"
		

	def getLicensingInfo(self, doc_license_aasociation_id):
		'''
		populates licensingInfo from database
		'''
		
		'''Create connection'''
		with ConfigParser.ConfigParser() as configParser:
			configParser.read("do_spdx.cfg")
			dbUserName   = configParser.get('Database','database_user')
			dbUserPass   = configParser.get('Database','database_pass')
			dbHost       = configParser.get('Database','database_host')
			dbName       = configParser.get('Database','database_name')

		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
			sqlCommand = """SELECT	dla.license_identifier,
									dla.license_name,
									dla.license_comments,
									l.extracted_text,
									l.license_cross_reference
	
							FROM doc_license_associations AS dla
							     INNER JOIN licenses AS l ON dla.license_id = l.id
		
							WHERE dla.id = ?"""
			dbCursor.execute(sqlCommand, doc_license_association_id)
	
			queryReturn = dbCursor.fetchone()

			self.licenseId 				= queryReturn.license_identifier
			self.licenseName 			= queryReturn.license_name
			self.licenseComment 		= queryReturn.license_comments
			self.extractedText 			= queryReturn.extracted_text
			self.licenseCrossReference 	= queryReturn.license_cross_reference
