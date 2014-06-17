#!/usr/bin/python

'''
Defines the creator info section of an spdx object.
'''
import MySQLdb
import datetime
import settings

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
        
		with MySQLdb.connect(host = settings.database_host, user = settings.database_user, passwd = settings.database_pass, db = settings.database_name) as dbCursor:
		
			'''Get next auto incriment value'''
			sqlCommand = 	"SHOW TABLE STATUS LIKE 'creators'"
			dbCursor.execute(sqlCommand)
			creatorId = dbCursor.fetchone()
			creatorId = creatorId[10]

			'''insert into creators table'''
			sqlCommand = 	"""INSERT INTO creators (generated_at, creator_comments, license_list_version, spdx_doc_id, creator, created_at, updated_at)
 					   VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""
			dbCursor.execute(sqlCommand,(self.creatorComment, self.licenseListVersion, spdx_doc_id, self.creator))
		
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
		
	def outputCreatorInfo_RDF(self):		
		print '<creator>' + self.creator + '</creator>'
		print '<created>' + str(self.created) + '</created>'
		if self.creatorComment != "":
			print '<rdfs:comment>' + self.creatorComment + '</rdfs:comment>'
		if self.licenseListVersion != "":
			print '<licenseListVersion>' + self.licenseListVersion + '</licenseListVersion>'
		
	def getCreatorInfo(self, creator_id, dbCursor):
		'''
		generates the creator structure from the database.
		'''

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
			self.creatorComment 		= creatorRow[2]
			self.licenseListVersion 	= creatorRow[3]
			self.creator			= creatorRow[5]
			self.created			= creatorRow[6]
		
	
