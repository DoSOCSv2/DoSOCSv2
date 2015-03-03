#!/usr/bin/python
'''
<SPDX-License-Identifier: Apache-2.0>
Copyright 2014 University of Nebraska at Omaha (UNO)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

'''
Command line interface for spdx object
'''

import sys
import os
import getopt
import spdx
import fileInfo
import licensingInfo
import reviewerInfo


def usage():
   print '''\
Usage: DoSPDX.py [OPTION]...

Options:
  -p, --packagePath=PATH      Package to run DoSOCS against
  --scan                      Scan the package specified by `-p'
  --print=FORMAT              Print SPDX document in specified format
                                (`tag', `json' or `rdf')
  --documentComment=TEXT      Specify SPDX document comment section
  --spdxDocId=ID              Generate SPDX document from database
                                (required if `-s' not specified)
  --creator=TEXT              Specify SPDX creator field
  --creatorComment=TEXT       Specify SPDX creator comment field
  --packageVersion=TEXT       Specify package version
  --packageDownloadLocation=TEXT
                              Specify package download location field
  --packageOriginator=TEXT    Specify package originator field
  --packageHomePage=TEXT      Specify package home page field
  --packageSourceInfo=TEXT    Specify package source information field
  --packageLicenseComments=TEXT
                              Specify license comments field
  --packageDescription=TEXT   Specify package description field
  --scanOption=SCANNER        Specify what scanner to use
                                (`fossology' to use FOSSology only)

Options taking a TEXT argument require double quotes around the argument.\
'''

def main(argv):
    progname = os.path.basename(sys.argv[0])
    '''Command line arguments.'''
    longopts = [
        "help",
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
        "scanOption=",
        "print=",
        "spdxDocId=",
        "scan"
    ]
    try:
        opts, args = getopt.getopt(argv, "hp:", longopts)
    except getopt.GetoptError as inst:
        print progname + ": " + inst.msg
        print progname + ": Try `" + progname + " --help' for more information."
        sys.exit(1)
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
    scanOption = ""
    output = ""
    scan = False
    spdxDocId = None

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
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
        elif opt == '--scanOption':
            scanOption = arg
        elif opt == '--print':
            output = arg
        elif opt in ('--scan'):
            scan = True
        elif opt == '--spdxDocId':
            spdxDocId = arg

    '''Validate package path'''
    if scan and (packagePath == None or not os.path.isfile(packagePath)):
        print progname + ": You must specify a valid package path"
        print progname + ": Try `" + progname + " --help' for more information."
        sys.exit(1)

    '''Create spdx object'''
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

    '''Execute requested commands'''
    result = True;
    if spdxDocId != None:
        result = spdxDoc.getSPDX(spdxDocId)

    if result == False:
        sys.exit()

    if scan == True:
        spdxDoc.generateSPDXDoc(scanOption)
        spdxDoc.insertSPDX()

    if output.lower() == 'tag':
        print spdxDoc.outputSPDX_TAG()
    elif output.lower() == 'rdf':
        print spdxDoc.outputSPDX_RDF()
    elif output.lower() == 'json':
        print spdxDoc.outputSPDX_JSON()

    if not opts:
        print progname + ": You must specify one of (`--scan', `--spdxDocId')"
        print progname + ": Try `" + progname + " --help' for more information."

if __name__ == "__main__":
    main(sys.argv[1:])
