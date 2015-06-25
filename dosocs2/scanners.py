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

The expected format is one class per scanner. Each class must have an
attribute 'name'; this is the name that will be attached to the raw scanner
output as stored in the database. It must also have a single method scan()
that returns a list of ScannerResult objects.
'''

from collections import namedtuple
from .config import config
import re
import subprocess

ScannerResult = namedtuple('ScannerResult', ('file_path', 'license'))

def nomos(filename):
    args = (config['nomos']['path'], filename)
    output = subprocess.check_output(args)
    licenses = []
    pattern = re.compile('File (.+?) contains license\(s\) (.+)')
    for line in output.split('\n'):
        m = re.match(pattern, line)
        if m is None:
            continue
        for subitem in m.group(2).split(','):
            result = ScannerResult(file_path=m.group(1), license=subitem)
            licenses.append(result)
    return [l for l in licenses if l.license != 'No_license_found']

def dummy(filename):
    return []

scanners = {
    'nomos': nomos,
    'dummy': dummy
    }
