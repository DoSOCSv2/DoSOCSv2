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


import string

from sqlalchemy.sql import select, and_

from . import schema as db


def insert(conn, table, params):
    query = table.insert().values(**params)
    result = conn.execute(query)
    [pkey] = result.inserted_primary_key
    return pkey


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


def store_license_scan_result(conn, scanner_name, scan_result, path_file_id_map):
    for path in scan_result:
        licenses_found = [
            lookup_or_add_license(conn, shortname, 'found by ' + scanner_name)
            for shortname in scan_result[path]
            ]
        for license in licenses_found:
            file_license_params = {
                'file_id': path_file_id_map[path],
                'license_id': license['license_id'],
                'extracted_text': '',
                }
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
                insert(conn, db.files_licenses, file_license_params)
