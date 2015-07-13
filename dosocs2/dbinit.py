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

'''dosocs2 database initialization.'''

from __future__ import print_function

import pkg_resources
import re
import sys
import urllib2
import uuid


def msg(text, **kwargs):
    print('dosocs2' + ': ' + text, **kwargs)
    sys.stdout.flush()


def errmsg(text, **kwargs):
    print('dosocs2' + ': ' + text, file=sys.stderr, **kwargs)
    sys.stdout.flush()


def load_file_types(db):
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
        db.file_types.insert(name=f)


def load_licenses(db, url='http://spdx.org/licenses/'):
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
            }
        db.licenses.insert(**license_params)
    return True


def load_creator_types(db):
    creator_types = (
        'Person',
        'Organization',
        'Tool'
        )
    for c in creator_types:
        db.creator_types.insert(name=c)


def load_annotation_types(db):
    annotation_types = (
        'REVIEW',
        'OTHER'
        )
    for a in annotation_types:
        db.annotation_types.insert(name=a)


def load_default_creator(db, creator_string):
    creator_type = (db.creator_types
        .filter(db.creator_types.name == 'Tool')
        .one()
        )
    creator_params = {
        'creator_type_id': creator_type.creator_type_id,
        'name': creator_string,
        'email': ''
        }
    db.creators.insert(**creator_params)


def load_relationship_types(db):
    relationship_types = (
        'DESCRIBES',
        'DESCRIBED_BY',
        'CONTAINS',
        'CONTAINED_BY',
        'GENERATES',
        'GENERATED_FROM',
        'ANCESTOR_OF',
        'DESCENDANT_OF',
        'VARIANT_OF',
        'DISTRIBUTION_ARTIFACT',
        'PATCH_FOR',
        'PATCH_APPLIED',
        'COPY_OF',
        'FILE_ADDED',
        'FILE_DELETED',
        'FILE_MODIFIED',
        'EXPANDED_FROM_ARCHIVE',
        'DYNAMIC_LINK',
        'STATIC_LINK',
        'DATA_FILE_OF',
        'TEST_CASE_OF',
        'BUILD_TOOL_OF',
        'DOCUMENTATION_OF',
        'OPTIONAL_COMPONENT_OF',
        'METAFILE_OF',
        'PACKAGE_OF',
        'AMENDS',
        'PREREQUISITE_FOR',
        'HAS_PREREQUISITE',
        'OTHER'
        )
    for rt in relationship_types:
        db.relationship_types.insert(name=rt)


def scrape_site(url):
    '''Scrape license info and return (url, name, shortname) tuples'''
    page_text = urllib2.urlopen(url).read()
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


def execute_sql_in_file(path, db):
    with open(path) as f:
        query = f.read()
    result = db.execute(query)
    return result


def drop_all_tables(db):
    filename = pkg_resources.resource_filename('dosocs2', 'sql/spdx_drop_tables.sql')
    return execute_sql_in_file(filename, db)


def create_all_tables(db):
    filename = pkg_resources.resource_filename('dosocs2', 'sql/spdx_create_tables.sql')
    return execute_sql_in_file(filename, db)


def drop_all_views(db):
    filename = pkg_resources.resource_filename('dosocs2', 'sql/spdx_drop_views.sql')
    return execute_sql_in_file(filename, db)


def create_all_views(db):
    filename = pkg_resources.resource_filename('dosocs2', 'sql/spdx_create_views.sql')
    return execute_sql_in_file(filename, db)


def initialize(db):
    url = 'http://spdx.org/licenses/'
    msg('dropping all views...', end='')
    result = dbinit.drop_all_views(db)
    print('ok.')
    msg('dropping all tables...', end='')
    result = dbinit.drop_all_tables(db)
    print('ok.')
    msg('creating all tables...', end='')
    result = dbinit.create_all_tables(db)
    print('ok.')
    msg('committing changes...', end='')
    db.commit()
    print('ok.')
    msg('creating all views...', end='')
    result = dbinit.create_all_views(db)
    print('ok.')
    msg('loading licenses...', end='')
    result = dbinit.load_licenses(db, url)
    if not result:
        errmsg('error!')
        errmsg('failed to download and load the license list')
        errmsg('check your connection to ' + url +
               ' and make sure it is the correct page'
               )
        return False
    else:
        print('ok.')
    msg('loading creator types...', end='')
    dbinit.load_creator_types(db)
    print('ok.')
    msg('loading default creator...', end='')
    dbinit.load_default_creator(db, 'dosocs2-' + __version__)
    print('ok.')
    msg('loading annotation types...', end='')
    dbinit.load_annotation_types(db)
    print('ok.')
    msg('loading file types...', end='')
    dbinit.load_file_types(db)
    print('ok.')
    msg('loading relationship types...', end='')
    dbinit.load_relationship_types(db)
    print('ok.')
    msg('committing changes...', end='')
    db.commit()
    print('ok.')
    return True
