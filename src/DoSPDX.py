#!/usr/bin/python

import sys
import os
import getopt
import spdx
import fileInfo
import licensingInfo
import reviewerInfo


def main(argv):
    opts, args = getopt.getopt(argv, "hp:", ["help",
                                            "packagePath=",
                                            "documentComment=",
                                            "creator=",
                                            "creatorComment=",
                                            "packageVersion=",
                                            "packageSupplier=",
                                            "packageDownloadLocation=",
                                            "packageOriginator=",
                                            "packageHomePage=",
                                            "packageSourceInfo=",
                                            "packageLicenseComments=",
                                            "packageDescription=",
                                            "print=",
                                            "spdxDocId=",
                                            "scan"])

    documentComment = ""
    packagePath = None
    creator = ""
    creatorComment = ""
    licenseListVersion = ""
    packageVersion = ""
    packageSupplier = ""
    packageOriginator = ""
    packageDownloadLocation = ""
    packageHomePage = ""
    packageSourceInfo = ""
    packageLicenseComments = ""
    packageDescription = ""
    output = ""
    scan = False
    spdxDocId = None

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
        elif opt in ('--scan'):
            scan = True
        elif opt == '--spdxDocId':
            spdxDocId = arg

    if scan and (packagePath == None or not os.path.isfile(packagePath)):
        raise Exception('Invalid Package path')

    spdxDoc = spdx.SPDX(documentComment=documentComment,
                        packagePath=packagePath,
                        creator=creator,
                        creatorComment=creatorComment,
                        licenseListVersion="1.19",
                           packageVersion=packageVersion,
                              packageSupplier=packageSupplier,
                           packageOriginator=packageOriginator,
                           packageDownloadLocation=packageDownloadLocation,
                        packageHomePage=packageHomePage,
                        packageSourceInfo=packageSourceInfo,
                        packageLicenseComments=packageLicenseComments,
                        packageDescription=packageDescription)

    if spdxDocId != None:
        result = spdxDoc.getSPDX(spdxDocId)

    if result == False:
        sys.exit()

    if scan == True:
        spdxDoc.generateSPDXDoc()
        spdxDoc.insertSPDX()

    if output.lower() == 'tag':
        print spdxDoc.outputSPDX_TAG()
    elif output.lower() == 'rdf':
        print spdxDoc.outputSPDX_RDF()
    elif output.lower() == 'json':
        spdxDoc.outputSPDX_JSON()

if __name__ == "__main__":
    main(sys.argv[1:])
