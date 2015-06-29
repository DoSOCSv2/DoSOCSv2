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

from collections import namedtuple
from .config import config
import re
import subprocess

ScannerResult = namedtuple('ScannerResult', ('file_path', 'license'))

def nomos(filename):
    ignore_pattern = config['nomos'].get('ignore')
    if ignore_pattern:
        if re.match(ignore_pattern, filename):
            return None
    args = (config['nomos']['path'], filename)
    output = subprocess.check_output(args)
    licenses = []
    pattern = 'File (.+?) contains license\(s\) (.+)'
    for line in output.split('\n'):
        m = re.match(pattern, line)
        if m is None:
            continue
        for subitem in m.group(2).split(','):
            result = ScannerResult(file_path=m.group(1), license=subitem)
            licenses.append(result)
    return [l for l in licenses if l.license != 'No_license_found']

def dummy(filename):
    return None

scanners = {
    'nomos': nomos,
    'dummy': dummy
    }
