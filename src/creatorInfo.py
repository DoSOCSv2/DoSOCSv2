#!/usr/bin/python

import _mysql
import ConfigParser
import datetime

class creatorInfo:
	def __init__(self, packagePath, creator = "", creatorComment = "", licenseListVersion = ""):	
		self.creator 		= creator
		self.created 	    	= datetime.datetime.now()
		self.creatorComment 	= creatorComment
		self.licenseListVersion = licenseListVersion
		
			
	def insertCreatorInfo(self, spdx_doc_id):
		'''
		inserts creatorInfo into the database
		'''

		creatorId = None
		'''Create connection'''
		with ConfigParser.ConfigParser("do_spdx.cfg") as configParser:
			configParser.read("do_spdx.cfg")
	        dbUserName   = configParser.get('Database','database_user')
	        dbUserPass   = configParser.get('Database','database_pass')
	        dbHost       = configParser.get('Database','database_host')
	        dbName       = configParser.get('Database','database_name')
        
		with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
		
			'''Get next auto incriment value'''
			sqlCommand = 	"SHOW TABLE STATUS LIKE 'creators'"
			dbCursor.execute(sqlCommand)
			creatorId = dbCursor.fetchone()
			creatorId = creatorId.Auto_increment

			'''insert into creators table'''
			sqlCommand = 	"""INSERT INTO creators (generated_at, creator_comments, license_list_version, spdx_doc_id, creator, created_at, updated_at)
 					   VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""
			dbCursor.execute(sqlCommand, self.creatorComment, self.licenseListVersion, spdx_doc_id, self.creator)
		
		return creatorId
				
	def outputCreatorInfo_TAG(self):
		'''
		outputs creatorInfo to stdout
		'''
		print "Creator: " + self.creator
		print "Created: " + str(self.created)
		if self.creatorComment != "":
			print "CreatorComment: " + self.creatorComment
		if self.licenseListVersion != "":
			print "LicenseListVersion: " + self.licenseListVersion
		
		
	def getCreatorInfo(self, creator_id):
		'''
		generates the creator structure from the database.
		'''

		'''Create connection'''
        with ConfigParser.ConfigParser() as configParser:
			configParser.read("do_spdx.cfg")
			dbUserName   = configParser.get('Database','database_user')
			dbUserPass   = configParser.get('Database','database_pass')
			dbHost       = configParser.get('Database','database_host')
			dbName       = configParser.get('Database','database_name')
			
			with MySQLdb.connect(host = dbHost, user = dbUserName, passwd = dbUserPass, db = dbName) as dbCursor:
				'''get creator info'''
				sqlCommand = 	"""SELECT id AS creator_id,
					      	  	  		  generated_at,
							     		  creator_comments,
							  			  license_list_version,
							  			  spdx_doc_id,
							  			  creator,
						 	  			  created_at,
							  			  updated_at
						  		   FROM creators
						  		   WHERE id = %s"""
				dbCursor.execute(sqlCommand,(creator_id))
			
				'''Get row of information'''
				creatorRow = dbCursor.fetchone()
				if creatorRow is not None:
					self.creatorComment 	= creatorRow.creator_comments
					self.licenseListVersion = creatorRow.license_list_version
					self.creator			= creatorRow.creator
					self.created			= creatorRow.generated_at
		
	
