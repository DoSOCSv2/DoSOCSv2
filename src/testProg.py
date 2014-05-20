#!/usr/bin/python

import spdx
import fileInfo
import licensingInfo
import reviewerInfo
import ConfigParser

def runTests():
	parser = ConfigParser.ConfigParser()
	parser.read("do_spdx.cfg")
	spdxDoc = spdx.SPDX(	documentComment 	= "Testing SQL inserts",
				packagePath             = "test.tar.bz",
      	               		creator                 = "Zac",
       	               		creatorComment          = "Creating test for sql inserts",
		                licenseListVersion      = "1.19",
       	                	packageVersion          = "1.0",
       	               		packageSupplier         = "apache",
       	                	packageOriginator       = "Apache",
                       		packageDownloadLocation = "http://mirror.metrocast.net/apache//httpd/httpd-2.4.9.tar.bz2",
                        	packageHomePage         = "http://httpd.apache.org/",
                        	packageSourceInfo       = "",
                        	packageLicenseComments  = "Apache 2.0 license",
                        	packageDescription      = "Hosts local content to the web")	
	files = fileInfo.fileInfo("test.txt") 
	licenses = licensingInfo.licensingInfo()
	reviewer = reviewerInfo.reviewerInfo()
	spdxDoc.licensingInfo.append(licenses)
	spdxDoc.fileInfo.append(files)
	spdxDoc.reviewerInfo.append(reviewer)
	spdxDoc.outputSPDX_TAG()
	spdxDoc.insertSPDX(dbHost = parser.get('Database', 'database_host'), dbUserName = parser.get('Database', 'database_user'), dbUserPass = parser.get('Database', 'database_pass'), dbName = parser.get('Database', 'database_name'))
runTests()


