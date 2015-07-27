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


import copy
import itertools
import os
import string

from sqlalchemy.sql import select, and_

from . import config
from . import queries
from . import schema as db
from . import util


def insert(conn, table, params):
    query = table.insert().values(**params)
    result = conn.execute(query)
    [pkey] = result.inserted_primary_key
    return pkey


def lookup_by_sha1(conn, table, sha1):
    '''Lookup row by SHA-1 sum and return the row, or None.'''
    # Freak occurence of sha1 collision probably won't happen.
    # But if it does, this will fail with 'too many values to unpack'
    # (although, you will have bigger problems then...)
    query = (
        select([table])
        .where(table.c.sha1 == sha1)
        )
    [result] = conn.execute(query).fetchall() or [None]
    if result is None:
        return result
    else:
        return dict(**result)


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


def create_file(conn, path, known_sha1):
    file_type_query = (
        select([db.file_types.c.file_type_id])
        .where(db.file_types.c.name == util.spdx_filetype(path))
        )
    file_type_id = conn.execute(file_type_query).fetchone()['file_type_id']
    new_file = {
        'sha1': known_sha1,
        'file_type_id': file_type_id,
        'copyright_text': None,
        'project_id': None,
        'comment': '',
        'notice': ''
        }
    new_file['file_id'] = insert(conn, db.files, new_file)
    return new_file


def store_scan_result(conn, scanner_name, scan_result, path_file_id_map):
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
            insert(conn, db.files_licenses, file_license_params)


def scan_file(conn, path, scanner, known_sha1=None):
    '''Scan file for licenses, and add it to the DB if it does not exist.

    Return the file object.

    If the file is cached, return the cached file object, and do not
    scan.
    '''
    sha1 = known_sha1 or util.sha1(path)
    file = lookup_by_sha1(conn, db.files, sha1)
    if file is not None:
        return file
    file = create_file(conn, path, sha1)
    scan_result = scanner.scan_file(path)
    store_scan_result(conn, scanner.name, scan_result, {path: file['file_id']})
    return file


def scan_directory(conn, path, scanner, name=None, version=None, comment=None,
                   file_name=None, sha1=None):
    # Passing sha1=None indicates a true directory, not a package
    ver_code, hashes, dir_code = util.get_dir_hashes(path)
    # Use calculated directory code and package verification code to see
    # if we have already scanned this one
    # (Not applicable to true packages)
    if sha1 is None:
        found_pkg_query = (
            select([db.packages])
            .where(
                and_(
                    db.packages.c.dosocs2_dir_code == dir_code,
                    db.packages.c.verification_code == ver_code
                    )
                )
            )
        [found_pkg] = conn.execute(found_pkg_query).fetchall() or [None]
        if found_pkg is not None:
            return found_pkg
    package = {
        'name': name or os.path.basename(os.path.abspath(path)),
        'version': version or '',
        'file_name': file_name or os.path.basename(os.path.abspath(path)),
        'supplier_id': None,
        'originator_id': None,
        'download_location': None,
        'verification_code': ver_code,
        'ver_code_excluded_file_id': None,
        'sha1': sha1, # None is permitted here, indicating a directory
        'home_page': None,
        'source_info': '',
        'concluded_license_id': None,
        'declared_license_id': None,
        'license_comment': '',
        'copyright_text': None,
        'summary': '',
        'description': '',
        'comment': '',
        'dosocs2_dir_code': None if sha1 is not None else dir_code
        }
    package['package_id'] = insert(conn, db.packages, package)
    for (filepath, sha1) in hashes.iteritems():
        fileobj = scan_file(conn, filepath, scanner, known_sha1=sha1)
        package_file_params = {
            'package_id': package['package_id'],
            'file_id': fileobj['file_id'],
            'concluded_license_id': None,
            'file_name': util.abs_to_rel(path, filepath),
            'license_comment': ''
            }
        insert(conn, db.packages_files, package_file_params)
    return package


def scan_package(conn, path, scanner, name=None, version=None, comment=None):
    '''Scan package for licenses. Add it and all files to the DB.

    Return the package object.

    Only scan if the package is not already cached (by SHA-1).
    '''
    if os.path.isdir(path):
        kwargs = {
            'path': path,
            'scanner': scanner,
            'name': name,
            'version': version,
            'comment': comment
            }
        return scan_directory(conn, **kwargs)
    sha1 = util.sha1(path)
    package = lookup_by_sha1(conn, db.packages, sha1)
    if package is not None:
        return package
    with util.tempextract(path) as (tempdir, relpaths):
        kwargs = {
            'path': tempdir,
            'scanner': scanner,
            'name': name or util.package_friendly_name(os.path.basename(path)),
            'version': version,
            'comment': comment,
            'file_name': os.path.basename(os.path.abspath(path)),
            'sha1': sha1
            }
        package = scan_directory(conn, **kwargs)
    return package


def create_document_namespace(conn, doc_name):
    suffix = util.friendly_namespace_suffix(doc_name)
    uri = config.config['dosocs2']['namespace_prefix'] + suffix
    doc_namespace = {'uri': uri}
    doc_namespace['document_namespace_id'] = insert(conn, db.document_namespaces, doc_namespace)
    return doc_namespace


def create_all_identifiers(conn, doc_namespace_id, package):
    all_files_query = (
        select([db.packages_files])
        .where(db.packages_files.c.package_id == package['package_id'])
        )
    identifier_ids = []
    package_id_params = {
        'document_namespace_id': doc_namespace_id,
        'package_id': package['package_id'],
        'id_string': util.gen_id_string('package', package['file_name'], package['sha1'])
        }
    for file in conn.execute(all_files_query):
        filesha1_query = (
            select([db.files.c.sha1])
            .where(db.files.c.file_id == file['file_id'])
            )
        filesha1 = conn.execute(filesha1_query).fetchone()['sha1']
        file_id_params = {
            'document_namespace_id': doc_namespace_id,
            'package_file_id': file['package_file_id'],
            'id_string': util.gen_id_string('file', file['file_name'], filesha1)
            }
        new_identifier_id = insert(conn, db.identifiers, file_id_params)
        identifier_ids.append(new_identifier_id)
    package_identifier_id = insert(conn, db.identifiers, package_id_params)
    identifier_ids.append(package_identifier_id)
    return identifier_ids


def create_relationship(conn, left_id, rel_type, right_id):
    relationship_params = {
        'left_identifier_id': left_id,
        'relationship_type_id': rel_type,
        'right_identifier_id': right_id,
        'relationship_comment': ''
    }
    insert(conn, db.relationships, relationship_params)


def autocreate_relationships(conn, docid):
    qs = (
        queries.auto_contains(docid),
        queries.auto_contained_by(docid),
        # queries.auto_describes(docid),
        # queries.auto_described_by(docid)
        )
    for q in qs:
        for row in conn.execute(q):
            kwargs = {
                'conn': conn,
                'left_id': row['left_identifier_id'],
                'rel_type': row['relationship_type_id'],
                'right_id': row['right_identifier_id']
                }
            create_relationship(**kwargs)


def create_document(conn, package, name=None, comment=None):
    data_license_query = (
        select([db.licenses.c.license_id])
        .where(db.licenses.c.short_name == 'CC0-1.0')
        )
    data_license_id = conn.execute(data_license_query).fetchone()['license_id']
    doc_name = name or package['name']
    doc_namespace_id = create_document_namespace(conn, doc_name)['document_namespace_id']
    new_document = {
        'data_license_id': data_license_id,
        'spdx_version': 'SPDX-2.0',
        'name': doc_name,
        'document_namespace_id': doc_namespace_id,
        'license_list_version': '2.0',  # TODO: dynamically fill from database table
        'creator_comment': name or '',
        'document_comment': comment or '',
        'package_id': package['package_id']
        }
    new_document_id = insert(conn, db.documents, new_document)
    new_document['document_id'] = new_document_id
    # default creator id should always be 1, because the default is
    # always the first creator row created.
    # TODO: don't hardcode this.
    document_creator_params = {
        'document_id': new_document_id,
        'creator_id': 1
        }
    insert(conn, db.documents_creators, document_creator_params)
    document_identifier_params = {
        'document_namespace_id': doc_namespace_id,
        'document_id': new_document_id,
        'id_string': 'SPDXRef-DOCUMENT'
        }
    # create all identifiers
    insert(conn, db.identifiers, document_identifier_params)
    create_all_identifiers(conn, doc_namespace_id, package)
    # TODO: create known relationships
    autocreate_relationships(conn, new_document_id)
    return new_document


def fetch(conn, table, pkey):
    [c] = list(table.primary_key)
    query = select([table]).where(c == pkey)
    [result] = conn.execute(query).fetchall() or [None]
    if result is None:
        return result
    else:
        return dict(**result)


def get_doc_by_package_id(conn, package_id):
    query = select([db.documents]).where(db.documents.c.package_id == package_id)
    # could potentially return more than one
    # but that's OK
    result = conn.execute(query).fetchone()
    if result is None:
        return result
    else:
        return dict(**result)
