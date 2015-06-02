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

import orm
import re
import requests
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
        'DOCUMENTATION',
        'SPDX',
        'OTHER'
        )
    for f in filetypes:
        session.add(orm.FileType(name=f))


def load_licenses(session, url='http://spdx.org/licenses/'):
    rows = scrape_site(url)
    sorted_rows = list(sorted(rows))
    if len(rows) == 0:
        return False
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
    return True


def load_creator_types(session):
    creator_types = (
        'Person',
        'Organization',
        'Tool'
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


def load_default_creator(session, creator_string):
    creator_type = (
        session.query(orm.CreatorType)
        .filter(orm.CreatorType.name == 'TOOL')
        .one()
        )
    creator_params = {
        'creator_type_id': creator_type.creator_type_id,
        'name': creator_string,
        'email': ''
        }
    session.add(orm.Creator(**creator_params))


def scrape_site(url):
    '''Scrape license info and return (url, name, shortname) tuples'''
    page_text = requests.get(url).text
    url_part = r'<tr>\s*<td><a href=\"(.*?)\".*?>'
    name_part = r'(.*?)</a></td>\s*.*?'
    shortname_part = r'<code property=\"spdx:licenseId\">(.*?)</code>'
    pattern_str = url_part + name_part + shortname_part
    pattern = re.compile(pattern_str)
    page_one_line = page_text.replace('\n', '')
    rows = pattern.findall(page_one_line)
    # reverse column order and append full url to first column
    completed_rows = [
        [row[2], row[1], (url + row[0][2:])]
        for row in rows
        ]
    return completed_rows


def execute_sql_in_file(path):
    with open(path) as f:
        query = f.read()
    result = orm.engine.execute(query)
    return result


def drop_all_tables():
    return execute_sql_in_file('sql/spdx20_drop.sql')


def create_all_tables():
    return execute_sql_in_file('sql/spdx20_create.sql')
