# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2015 University of Nebraska Omaha and other contributors.

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

'''Interfaces to external scanning tools.

The expected format is one function per scanner, that must either return
a list of ScannerResult objects, or None:

scan(filename) -> [ScannerResult] or None

A return value of None indicates that the input file was not scanned. A
return value of [] indicates that the input file was scanned but no license
information was found.
'''

import os
import re
import subprocess
from collections import namedtuple

from . import util
from .config import config

ScannerResult = namedtuple('ScannerResult', ('file_path', 'license'))
_nomos_pattern = re.compile('File (.+?) contains license\(s\) (.+)')


def nomos(filename):
    ignore_pattern = config['nomos'].get('ignore')
    if ignore_pattern:
        if re.match(ignore_pattern, filename):
            return None
    args = (config['nomos']['path'], filename)
    output = subprocess.check_output(args)
    licenses = []
    for line in output.split('\n'):
        m = re.match(_nomos_pattern, line)
        if m is None:
            continue
        for subitem in m.group(2).split(','):
            result = ScannerResult(file_path=m.group(1), license=subitem)
            licenses.append(result)
    return [l for l in licenses if l.license != 'No_license_found']


def nomos_deep(filename):
    if util.archive_type(filename):
        results = []
        with util.tempextract(filename) as (tempdir, relpaths):
            abspaths = [os.path.join(tempdir, r) for r in relpaths]
            for path in abspaths:
                if not os.path.isfile(path):
                    continue
                else:
                    results += nomos(path)
            return list(set(r._replace(file_path=filename) for r in results))
    else:
        return nomos(filename)


def nomos_poms_only(filename):
    if filename == 'pom.xml' or filename.endswith('.pom'):
        return nomos(filename)
    else:
        return None

def dummy(filename):
    return None

scanners = {
    'nomos': nomos,
    'nomos_deep': nomos_deep,
    'nomos_poms_only': nomos_poms_only,
    'dummy': dummy
    }
