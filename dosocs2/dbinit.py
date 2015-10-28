# Copyright (C) 2015 University of Nebraska at Omaha
#
# This file is part of dosocs2.
#
# dosocs2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# dosocs2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dosocs2.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0+

'''dosocs2 database initialization.'''

from __future__ import print_function

import re
import sys
import urllib2

from sqlalchemy.sql import select

from . import schema as db


def msg(text, **kwargs):
    print('dosocs2' + ': ' + text, **kwargs)
    sys.stdout.flush()


def errmsg(text, **kwargs):
    print('dosocs2' + ': ' + text, file=sys.stderr, **kwargs)
    sys.stdout.flush()


def load_file_types(conn):
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
        conn.execute(db.file_types.insert().values(name=f))


def load_licenses(conn, url='http://spdx.org/licenses/'):
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
        conn.execute(db.licenses.insert().values(**license_params))
    return True


def load_creator_types(conn):
    creator_types = (
        'Person',
        'Organization',
        'Tool'
        )
    for c in creator_types:
        conn.execute(db.creator_types.insert().values(name=c))


def load_annotation_types(conn):
    annotation_types = (
        'REVIEW',
        'OTHER'
        )
    for a in annotation_types:
        conn.execute(db.annotation_types.insert().values(name=a))


def load_default_creator(conn, creator_string):
    query = (
        select([db.creator_types.c.creator_type_id])
        .where(db.creator_types.c.name == 'Tool')
        )
    creator_type_id = conn.execute(query).fetchone()['creator_type_id']
    creator_params = {
        'creator_type_id': creator_type_id,
        'name': creator_string,
        'email': ''
        }
    conn.execute(db.creators.insert().values(**creator_params))


def load_relationship_types(conn):
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
        conn.execute(db.relationship_types.insert().values(name=rt))


def scrape_site(url):
    '''Scrape license info and return (url, name, shortname) tuples'''
    page_text = urllib2.urlopen(url).read()
    url_part = r'<tr>\s*<td><a href=\"(.*?)\".*?>'
    name_part = r'(.*?)</a></td>\s*.*?'
    shortname_part = r'<code property=\"spdx:licenseId\">(.*?)</code>'
    pattern_str = url_part + name_part + shortname_part
    pattern = re.compile(pattern_str)
    page_one_line = page_text.replace('\n', '').replace('&quot;', '"')
    rows = pattern.findall(page_one_line)
    # reverse column order and append full url to first column
    completed_rows = [[
        row[2],                         # short name
        row[1],                         # friendly name
        (url + row[0][2:])]             # cross ref
        for row in rows
        ]
    return completed_rows


def initialize(engine, dosocs2_version):
    url = 'http://spdx.org/licenses/'
    msg('dropping and creating all tables...', end='')
    db.meta.drop_all(engine)
    db.meta.create_all(engine)
    print('ok.')
    with engine.begin() as conn:
        msg('loading licenses...', end='')
        result = load_licenses(conn, url)
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
        load_creator_types(conn)
        print('ok.')
        msg('loading default creator...', end='')
        load_default_creator(conn, 'dosocs2-' + dosocs2_version)
        print('ok.')
        msg('loading annotation types...', end='')
        load_annotation_types(conn)
        print('ok.')
        msg('loading file types...', end='')
        load_file_types(conn)
        print('ok.')
        msg('loading relationship types...', end='')
        load_relationship_types(conn)
        print('ok.')
        msg('committing changes...', end='')
    print('ok.')
    return True
