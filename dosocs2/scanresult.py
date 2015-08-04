# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2014-2015 University of Nebraska at Omaha (UNO) and other
# contributors.

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
