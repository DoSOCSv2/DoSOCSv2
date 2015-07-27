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

#!/usr/bin/env python2

from __future__ import print_function, unicode_literals

import xmltodict
import re
from collections import OrderedDict


def as_list(item):
    if isinstance(item, list):
        return item
    else:
        return [item]


def extract_cpe(item):
    if isinstance(item, OrderedDict):
        return item['#text']
    else:
        return item


def strip_whitespace(s):
    return re.sub(r'(\n|\s+)', r' ', s)


def get_cpes(dep):
    idents = as_list(dep.get('identifiers', {}).get('identifier', []))
    cpes = []
    for ident in idents:
        if ident['@type'] == 'cpe':
            cpes.append({
                'cpe': ident['name'],
                'confidence': ident['@confidence'],
                'url': ident.get('url', '')
                })
    return cpes


def parse_dependency_xml(xml_text):
    x = xmltodict.parse(xml_text)
    deps = []
    root_deps = x['analysis']['dependencies'] or {}
    for dep in as_list(root_deps.get('dependency', list())):
        this_vulns = []
        if 'vulnerabilities' in dep:
            for vuln in as_list(dep['vulnerabilities']['vulnerability']):
                v = {
                    'name': vuln['name'],
                    'description': vuln.get('description', ''),
                    'severity': vuln.get('severity', 'N/A'),
                    'cvssScore': vuln.get('cvssScore', '0.0'),
                    # 'cpes': [extract_cpe(cpe) for cpe in as_list(vuln['vulnerableSoftware']['software'])]
                    }
                this_vulns.append(v)
        deps.append({
            'sha1': dep['sha1'],
            'vulnerabilities': this_vulns,
            'cpes': get_cpes(dep)
            })
    return deps


class DependencyCheck():

    name = 'dependency_check'

    def __init__(self):
        self.exec_path = config['dependency_check']['path']

    def scan_directory(self, path):
        with util.tempdir() as tempdir:
            args = [
                self.exec_path,
                '--out', tempdir,
                '--format', 'XML',
                '--scan', path,
                '--app', 'none'
                ]
            subprocess.check_call(args)
            with open(os.path.join(tempdir, 'dependency-check-report.xml')) as f:
                xml_data = f.read()
        result = parse_dependency_xml(xml_data)
        return result
