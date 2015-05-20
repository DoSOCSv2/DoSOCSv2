#!/usr/bin/env python2

# <SPDX-License-Identifier: Apache-2.0>
# Copyright 2014 University of Nebraska at Omaha (UNO)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Usage: DoSPDX.py [--help] [options] (FILE | -i DOCID)

Options:
  -i, --doc-id=DOCID          Generate SPDX document from database
                                (required if FILE argument not specified)
  -n, --no-scan               Don't scan the package if SPDX data has not
                                already been generated
  -p, --print=FORMAT          Print SPDX document in specified format
                                (`tag', `json' or `rdf')
  --comment=TEXT              Specify SPDX document comment section
  --creator=TEXT              Specify SPDX creator field
  --creator-comment=TEXT      Specify SPDX creator comment field
  --supplier=TEXT             Specify package supplier field
  --package-version=TEXT      Specify package version field
  --download-location=TEXT    Specify package download location field
  --originator=TEXT           Specify package originator field
  --home-page=TEXT            Specify package home page field
  --source-info=TEXT          Specify package source information field
  --license-comments=TEXT     Specify license comments field
  --description=TEXT          Specify package description field

Options taking a TEXT argument require double quotes around the argument.\
'''


import docopt
import sys
import os
import spdx
import fileInfo
import licensingInfo
import reviewerInfo


def extract_fields(argv):
    fields = {
        'documentComment': argv['--comment'],
        'creator': argv['--creator'],
        'creatorComment': argv['--creator-comment'],
        'packageVersion': argv['--package-version'],
        'packageSupplier': argv['--supplier'],
        'packageOriginator': argv['--originator'],
        'packageDownloadLocation': argv['--download-location'],
        'packageHomePage': argv['--home-page'],
        'packageSourceInfo': argv['--source-info'],
        'packageLicenseComments': argv['--license-comments'],
        'packageDescription': argv['--description']
    }
    for key in fields:
        fields[key] = fields[key] or ''
    return fields


def main():
    progname = os.path.basename(sys.argv[0])
    argv = docopt.docopt(doc=__doc__, version='0.0.1-dev')

    if argv['--doc-id'] is None and argv['FILE'] is None:
        print progname + ": You must specify a file or document ID"
        print progname + ": Try `" + progname + " --help' for more information."
        sys.exit(1)

    fields = extract_fields(argv)
    package = argv['FILE']
    docid = argv['--doc-id']
    scan = not argv['--no-scan']
    output_format = argv['--print']

    if output_format not in ('json', 'tag', 'rdf', None):
        print progname + ": Unknown output format '" + output_format + "'"
        print progname + ": Try `" + progname + " --help' for more information."
        sys.exit(1)

    '''Create spdx object'''
    spdxDoc = spdx.SPDX(packagePath=package,
                        licenseListVersion="1.19",
                        **fields
                        )

    '''Execute requested commands'''
    result = True
    if docid is not None:
        result = spdxDoc.getSPDX(docid)

    if result is False:
        sys.exit(1)

    if docid is None and scan:
        spdxDoc.generateSPDXDoc()
        spdxDoc.insertSPDX()
    # else...

    if output_format is not None:
        print spdxDoc.as_string(output_format)


if __name__ == "__main__":
    main()
