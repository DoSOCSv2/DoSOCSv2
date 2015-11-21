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

import json
import string

from sqlalchemy.sql import select, and_, update

from . import schema as db
from .spdxdb import insert, bulk_insert


def lookup_license(conn, short_name):
    query = (
        select([db.licenses])
        .where(db.licenses.c.short_name == short_name)
        )
    [result] = conn.execute(query).fetchall() or [None]
    if result is None:
        return result
    else:
        return dict(**result)


def lookup_or_add_license(conn, short_name, comment=None):
    '''Add license to the database if it does not exist.

    Return the new or existing license object in any case.
    '''
    transtable = string.maketrans('()[]<>', '------')
    short_name = string.translate(short_name, transtable)
    existing_license = lookup_license(conn, short_name)
    if existing_license is not None:
        return existing_license
    new_license = {
        # correct long name is never known for found licenses
        'name': None,
        'short_name': short_name,
        'cross_reference': '',
        'comment': comment or '',
        'is_spdx_official': False,
        }
    new_license['license_id'] = insert(conn, db.licenses, new_license)
    return new_license


def add_file_licenses(conn, rows):
    to_add = {}
    for file_license_params in rows:
        query = (
            select([db.files_licenses])
            .where(
                and_(
                    db.files_licenses.c.file_id == file_license_params['file_id'],
                    db.files_licenses.c.license_id == file_license_params['license_id']
                    )
                )
            )
        [already_exists] = conn.execute(query).fetchall() or [None]
        if already_exists is None:
            
            key = file_license_params['file_id'], file_license_params['license_id']
            to_add[key] = file_license_params
    bulk_insert(conn, db.files_licenses, list(to_add.values()))

def add_file_copyright(conn, file_id, text):
    query = update(db.files).values({'copyright_text': text}).where(db.files.c.file_id == file_id)
    conn.execute(query)

def add_cpes(conn, package_id, cpes):
    json_text = json.dumps(cpes)
    query = update(db.packages).values({'comment': json_text}).where(db.packages.c.package_id == package_id)
    conn.execute(query)
