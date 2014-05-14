#!/usr/bin/python

import hashlib

class checksum:

	@staticmethod
	def getChecksum(filePath):
		with open(filePath, 'rb') as fileIn:
			fileSha1 = sha1()
			fileSha1.update(fileIn.read())
			return fileSha1.hexdigest()
	
