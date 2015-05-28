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

import orm
import re
import subprocess
import sys
import uuid


def load_file_types(session):
    filetypes = (
        'SOURCE',
        'BINARY',
        'ARCHIVE',
        'APPLICATION',
        'AUDIO',
        'IMAGE',
        'TEXT',
        'VIDEO',
        'DOCUMENTATION'
        )
    for f in filetypes:
        session.add(orm.FileType(name=f))


def load_licenses(session):
    rows = scrape_site()
    sorted_rows = list(sorted(rows))
    for shortname, name, url in sorted_rows:
        license_params = {
            'name': name,
            'short_name': shortname,
            'cross_reference': url,
            'comment': '',
            'is_spdx_official': True,
            'license_identifier': 'LicenseRef-' + str(uuid.uuid4())
            }
        session.add(orm.License(**license_params))


def load_creator_types(session):
    creator_types = (
        'PERSON',
        'ORGANIZATION',
        'TOOL'
        )
    for c in creator_types:
        session.add(orm.CreatorType(name=c))


def load_annotation_types(session):
    annotation_types = (
        'REVIEW',
        'OTHER'
        )
    for a in annotation_types:
        session.add(orm.AnnotationType(name=a))


def scrape(page_text):
    '''Scrape license info and return (url, name, shortname) tuples'''
    url_part = r'<tr>\s*<td><a href=\"(.*?)\".*?>'
    name_part = r'(.*?)</a></td>\s*.*?'
    shortname_part = r'<code property=\"spdx:licenseId\">(.*?)</code>'
    pattern_str = url_part + name_part + shortname_part
    pattern = re.compile(pattern_str)
    page_one_line = page_text.replace('\n', '')
    rows = pattern.findall(page_one_line)
    return rows


def scrape_site(url='http://spdx.org/licenses/'):
    page_text = subprocess.check_output(['curl', url])
    rows = scrape(page_text)
    # reverse column order and append full url to first column
    completed_rows = [[row[2], row[1], (url + row[0][2:])]
                      for row in rows
                      ]
    return completed_rows


def main():
    session = orm.Session()
    load_licenses(session)
    load_creator_types(session)
    load_annotation_types(session)
    load_file_types(session)
    session.commit()
    session.close()
