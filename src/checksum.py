#!/usr/bin/python
'''
Defines the checkum object for files.
'''

import hashlib

class checksum:

	def getChecksum(filePath):
		with open(filePath, 'rb') as fileIn:
			fileSha1 = sha1()
			fileSha1.update(fileIn.read())
			return fileSha1.hexdigest()
	
