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

scan_file() and scan_directory() must return a dictionary mapping a relative
file path (starting with '.') to a set of license short names. These license
names do not necessarily have to be on the SPDX license list.

scan_file(path) -> {str: {str}} or None
scan_directory(path) -> {str: {str}} or None
'''

import os
import re
import subprocess
from collections import defaultdict

from . import util
from .config import config


class Scanner(object):

    name = None

    def __init__(self):
        raise NotImplementedError

    def scan_file(path):
        raise NotImplementedError

    def scan_directory(path):
        raise NotImplementedError


class Nomos(Scanner):

    name = 'nomos'

    def __init__(self):
        self.exec_path = config['nomos']['path']
        self.search_pattern = re.compile(r'File (.+?) contains license\(s\) (.+)')
        self.parallel = config['nomos'].get('parallel') or '2'

    def scan_file(self, path):
        args = (self.exec_path, '-n', self.parallel, '-l', path)
        output = subprocess.check_output(args)
        scan_result = set()
        for line in output.split('\n'):
            m = re.match(self.search_pattern, line)
            if m is None:
                continue
            scan_result.update({
                lic_name
                for lic_name in m.group(2).split(',')
                if lic_name != 'No_license_found'
                })
        return {path: scan_result}

    def scan_directory(self, path):
        args = (self.exec_path, '-l', '-n', self.parallel, '-d', path)
        output = subprocess.check_output(args)
        scan_result = defaultdict(set) 
        for line in output.split('\n'):
            m = re.match(self.search_pattern, line)
            if m is None:
                continue
            scan_result['path'].update({
                lic_name
                for lic_name in m.group(2).split(',')
                if 'No_license_found' not in lic_name
                })
        return dict(scan_result)


class NomosDeep(Scanner):

    name = 'nomos_deep'

    def __init__(self):
        self._nomos = Nomos()

    def scan_file(self, path):
        if util.archive_type(path):
            scan_result = set()
            with util.tempextract(path) as (tempdir, relpaths):
                unfiltered_results = self._nomos.scan_directory(tempdir)
            for this_result in unfiltered_results.values():
                scan_result.update(this_result)
            return {path: scan_result}
        else:
            return self._nomos.scan_file(path)


class NomosPomsOnly(Scanner):

    name = 'nomos_poms_only'

    def __init__(self):
        self._nomos = Nomos()

    def scan_file(path):
        if path == 'pom.xml' or path.endswith('.pom'):
            return self._nomos.scan_file(path)
        else:
            return {}


class Dummy(Scanner):

    name = 'dummy'

    def __init__(self):
        pass

    def scan_file(path):
        return {}

    def scan_directory(path):
        return {}


scanners = {
    'nomos': Nomos,
    'nomos_deep': NomosDeep,
    'nomos_poms_only': NomosPomsOnly,
    'dummy': Dummy
    }
