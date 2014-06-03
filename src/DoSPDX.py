#!/usr/bin/python

import sys
import os
import getopt
import spdx
import fileInfo
import licensingInfo
import reviewerInfo

def main(argv):
	opts, args = getopt.getopt(argv, "hp:s", ["help", "packagePath=", "documentComment=", "creator=", "creatorComment=", "packageVersion=", "packageSupplier=", "packageDownloadLocation=", "packageOriginator=", 
						  "packageHomePage=", "packageSourceInfo=", "packageLicenseComments=", "packageDescription=", "print=", "scan"])
	
	
	documentComment 	= ""
	packagePath     	= ""
	creator         	= ""
	creatorComment  	= ""
	licenseListVersion 	= ""
	packageVersion		= ""
	packageSupplier		= ""
	packageOriginator	= ""
	packageDownloadLocation = ""
	packageHomePage		= ""
	packageSourceInfo	= ""
	packageLicenseComments  = ""
	packageDescription	= ""
	output 			= ""
	scan			= False

	for opt, arg in opts:
		if opt == '-h':
			print "Help Documentation"
		elif opt in ('-p', '--packagePath'): 
			packagePath = arg
		elif opt == '--documentComment':
			documentComment = arg
		elif opt == '--creator':
			creator = arg
		elif opt == '--creatorComment':
			creatorComment = arg
		elif opt == '--packageVersion':
			packageVersion = arg
		elif opt == '--packageSupplier':
			packageSupplier = arg
		elif opt == '--packageDownloadLocation':
			packageDownloadLocation = arg
		elif opt == '--packageOriginator':
			packageOriginator = arg
		elif opt == '--packageHomePage':
			packageHomePage = arg
		elif opt == '--packageSourceInfo':
			packageSourceInfo = arg
		elif opt == '--packageLicenseComments':
			packageLicenseComments = arg
		elif opt == '--packageDescription':
			packageDescription = arg
		elif opt == '--print':
			output = arg
		elif opt == '--scan':
			scan = True
	
	spdxDoc = spdx.SPDX(	documentComment 	= documentComment,
				packagePath             = packagePath,
      	               		creator                 = creator,
       	               		creatorComment          = creatorComment,
		                licenseListVersion      = "1.19",
       	                	packageVersion          = packageVersion,
       	               		packageSupplier         = packageSupplier,
       	                	packageOriginator       = packageOriginator,
                       		packageDownloadLocation = packageDownloadLocation,
                        	packageHomePage         = packageHomePage,
                        	packageSourceInfo       = packageSourceInfo,
                        	packageLicenseComments  = packageLicenseComments,
                        	packageDescription      = packageDescription)	

	if scan and packagePath == "" or not os.path.isfile(packagepath):
		raise Exception('Invalid package path.')
				

	if scan:
        	spdxDoc.generateSPDXDoc()
                spdxDoc.insertSPDX()

	if output.lower() == 'tag':
		spdxDoc.ouputSPDX_TAG()
	elif output.lower() == 'rdf':
		spdxDoc.outputSPDX_RDF()
	elif output.lower() == 'json':
		spdxDoc.outputSPDX_JSON()

if __name__ == "__main__":
	main(sys.argv[1:])


