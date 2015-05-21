# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2015 doSOCS contributors.

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

import re
import settings
import subprocess

class nomos:
    name = 'nomos'
    @staticmethod
    def scan(filename):
        args = (settings.scanner['nomos'], filename)
        output = subprocess.check_output(args)
        licenses = []
        pattern = re.compile('File (.+?) contains license\(s\) (.+)')
        for line in output.split('\n'):
            m = re.match(pattern, line)
            if m is None:
                continue
            for subitem in m.group(2).split(','):
                licenses.append((m.group(1), subitem))
        return licenses
